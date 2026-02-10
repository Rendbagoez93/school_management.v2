"""
Academic Year Orchestrator Service

This is the ONLY place where AcademicYear, AcademicYearSetup, and Grade 
are allowed to interact with each other.

This service orchestrates:
- Academic year lifecycle transitions (SETUP -> ENROLLMENT -> ACTIVE -> COMPLETED)
- Setup progress tracking and validation
- Grade creation and management during setup
- Student enrollment coordination
- Import task tracking and completion

Each model owns its own responsibilities:
- AcademicYear: Owns lifecycle status, dates, deployment type
- AcademicYearSetup: Owns setup progress, import tracking
- Grade: Owns class structure, student membership
- ImportTask: Owns import progress tracking

The orchestrator is the brain that coordinates everything.
"""

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from applications.school_management.academic_management.models import AcademicYear, StudentEnrollment
from applications.school_management.grade_management.models import Grade
from applications.school_management.grade_management.grade_factory import GradeFactory
from applications.academic_setup.models import AcademicYearSetup, ImportTask
from config.roles import RoleEnum


class AcademicYearOrchestrator:
    """
    The Pipeline Brain - orchestrates all interactions between
    AcademicYear, AcademicYearSetup, and Grade.
    """

    # ========================================================================
    # SECTION 1: ACADEMIC YEAR LIFECYCLE MANAGEMENT
    # ========================================================================

    @staticmethod
    @transaction.atomic
    def create_academic_year(
        name: str,
        start_date,
        end_date,
        deployment_type: str,
        enrollment_start_date=None,
        enrollment_end_date=None,
    ) -> AcademicYear:
        # Create the academic year in SETUP status
        academic_year = AcademicYear.objects.create(
            name=name,
            start_date=start_date,
            end_date=end_date,
            deployment_type=deployment_type,
            status=AcademicYear.Status.SETUP,
            setup_completed=False,
            enrollment_start_date=enrollment_start_date,
            enrollment_end_date=enrollment_end_date,
        )

        # Create the setup tracker
        AcademicYearSetup.objects.create(
            academic_year=academic_year,
            current_step=AcademicYearSetup.SetupSteps.BASIC_INFO,
        )

        return academic_year

    @staticmethod
    @transaction.atomic
    def transition_to_enrollment(academic_year: AcademicYear) -> None:

        if academic_year.status != AcademicYear.Status.SETUP:
            raise ValidationError(f"Cannot transition to ENROLLMENT from {academic_year.get_status_display()}")

        if not AcademicYearOrchestrator.is_setup_complete(academic_year):
            raise ValidationError("Setup must be complete before transitioning to ENROLLMENT")

        if academic_year.deployment_type == AcademicYear.DeploymentType.MID_YEAR:
            raise ValidationError("Mid-year deployment should transition directly to ACTIVE")

        # Update status
        academic_year.status = AcademicYear.Status.ENROLLMENT
        academic_year.setup_completed = True
        academic_year.save()

    @staticmethod
    @transaction.atomic
    def transition_to_active(academic_year: AcademicYear) -> None:

        if academic_year.status == AcademicYear.Status.SETUP:
            # Only mid-year can go directly from SETUP to ACTIVE
            if academic_year.deployment_type != AcademicYear.DeploymentType.MID_YEAR:
                raise ValidationError("Fresh start must go through ENROLLMENT phase")
            
            if not AcademicYearOrchestrator.is_setup_complete(academic_year):
                raise ValidationError("Setup must be complete before transitioning to ACTIVE")
        
        elif academic_year.status == AcademicYear.Status.ENROLLMENT:
            # Fresh start transitioning from ENROLLMENT to ACTIVE
            if academic_year.deployment_type != AcademicYear.DeploymentType.FRESH_START:
                raise ValidationError("Only fresh start should have ENROLLMENT phase")
        
        elif academic_year.status == AcademicYear.Status.ACTIVE:
            # Already active, nothing to do
            return
        
        else:
            raise ValidationError(f"Cannot transition to ACTIVE from {academic_year.get_status_display()}")

        # Update status
        academic_year.status = AcademicYear.Status.ACTIVE
        academic_year.setup_completed = True
        academic_year.save()

    @staticmethod
    @transaction.atomic
    def transition_to_completed(academic_year: AcademicYear) -> None:

        if academic_year.status == AcademicYear.Status.COMPLETED:
            return  # Already completed

        academic_year.status = AcademicYear.Status.COMPLETED
        academic_year.is_active = False
        academic_year.save()

    # ========================================================================
    # SECTION 2: SETUP PROGRESS MANAGEMENT
    # ========================================================================

    @staticmethod
    def get_required_steps(academic_year: AcademicYear) -> list[str]:
        steps = AcademicYearSetup.SetupSteps

        if academic_year.deployment_type == AcademicYear.DeploymentType.FRESH_START:
            return [
                steps.BASIC_INFO,
                steps.IMPORT_GRADES,
                steps.IMPORT_STUDENTS,
                steps.ASSIGN_CLASSROOMS,
                steps.REVIEW,
            ]
        else:  # MID_YEAR
            return [
                steps.BASIC_INFO,
                steps.IMPORT_GRADES,
                steps.IMPORT_STUDENTS,
                steps.ASSIGN_CLASSROOMS,
                steps.REVIEW,
            ]

    @staticmethod
    def get_completion_percentage(academic_year: AcademicYear) -> float:
        """Calculate setup completion percentage."""
        try:
            setup = academic_year.setup_progress
        except AcademicYearSetup.DoesNotExist:
            return 0.0

        required_steps = AcademicYearOrchestrator.get_required_steps(academic_year)
        if not required_steps:
            return 0.0

        status_map = {
            AcademicYearSetup.SetupSteps.BASIC_INFO: setup.basic_info_completed,
            AcademicYearSetup.SetupSteps.IMPORT_GRADES: setup.import_grades_completed,
            AcademicYearSetup.SetupSteps.IMPORT_STUDENTS: setup.import_students_completed,
            AcademicYearSetup.SetupSteps.ASSIGN_CLASSROOMS: setup.assign_classrooms_completed,
            AcademicYearSetup.SetupSteps.REVIEW: setup.review_completed,
        }

        completed_steps = sum(1 for step in required_steps if status_map.get(step, False))
        return (completed_steps / len(required_steps)) * 100

    @staticmethod
    def is_setup_complete(academic_year: AcademicYear) -> bool:
        try:
            setup = academic_year.setup_progress
        except AcademicYearSetup.DoesNotExist:
            return False

        return setup.is_complete()

    @staticmethod
    @transaction.atomic
    def mark_step_complete(
        academic_year: AcademicYear,
        step: str,
        import_method: str | None = None,
    ) -> None:
        """
        Mark a setup step as complete.
        
        Args:
            academic_year: The academic year being set up
            step: The step to mark complete (from SetupSteps choices)
            import_method: The import method used (for import steps)
        """
        setup = academic_year.setup_progress
        steps = AcademicYearSetup.SetupSteps

        if step == steps.BASIC_INFO:
            setup.basic_info_completed = True
            setup.current_step = steps.IMPORT_GRADES

        elif step == steps.IMPORT_GRADES:
            if import_method:
                setup.grades_import_method = import_method
            setup.import_grades_completed = True
            setup.current_step = steps.IMPORT_STUDENTS

        elif step == steps.IMPORT_STUDENTS:
            if import_method:
                setup.students_import_method = import_method
            setup.import_students_completed = True
            setup.current_step = steps.ASSIGN_CLASSROOMS

        elif step == steps.ASSIGN_CLASSROOMS:
            if import_method:
                setup.classrooms_import_method = import_method
            setup.assign_classrooms_completed = True
            setup.current_step = steps.REVIEW

        elif step == steps.REVIEW:
            setup.review_completed = True
            setup.current_step = steps.COMPLETED

        else:
            raise ValidationError(f"Invalid setup step: {step}")

        setup.save()

    # ========================================================================
    # SECTION 3: GRADE MANAGEMENT
    # ========================================================================

    @staticmethod
    @transaction.atomic
    def create_grade(
        academic_year: AcademicYear,
        name: str,
        grade: str,
        grade_type: str = "",
        grade_subtype: str = "",
        description: str = "",
    ) -> Grade:
        """
        Create a new grade/class for an academic year.
        
        This should typically be done during the IMPORT_GRADES step.
        Delegates to GradeFactory for actual creation.
        """
        return GradeFactory.create_grade(
            academic_year=academic_year,
            name=name,
            grade=grade,
            grade_type=grade_type,
            grade_subtype=grade_subtype,
            description=description,
        )

    @staticmethod
    @transaction.atomic
    def bulk_create_grades(academic_year: AcademicYear, grades_data: list[dict]) -> list[Grade]:
        return GradeFactory.bulk_create_grades(academic_year, grades_data)

    # ========================================================================
    # SECTION 4: STUDENT ENROLLMENT MANAGEMENT
    # ========================================================================

    @staticmethod
    @transaction.atomic
    def enroll_student(grade: Grade, student) -> StudentEnrollment:
        # Validate student has STUDENT role
        if not student.groups.filter(name=RoleEnum.STUDENT.value).exists():
            raise ValidationError("User must have STUDENT role to be enrolled")

        # Validate academic year status
        if grade.academic_year.status not in [
            AcademicYear.Status.SETUP,
            AcademicYear.Status.ENROLLMENT,
            AcademicYear.Status.ACTIVE,
        ]:
            raise ValidationError(
                f"Cannot enroll students when academic year is {grade.academic_year.get_status_display()}"
            )

        # Check if student is already enrolled in this academic year
        existing_enrollment = StudentEnrollment.objects.filter(
            student=student,
            academic_year=grade.academic_year,
            is_deleted=False,
        ).first()

        if existing_enrollment:
            if existing_enrollment.grade == grade:
                # Already enrolled in this grade, return existing
                return existing_enrollment
            else:
                raise ValidationError(
                    f"Student is already enrolled in {existing_enrollment.grade.name} "
                    f"for {grade.academic_year.name}"
                )

        # Create enrollment
        enrollment = StudentEnrollment.objects.create(
            student=student,
            grade=grade,
            academic_year=grade.academic_year,
        )

        return enrollment

    @staticmethod
    @transaction.atomic
    def unenroll_student(grade: Grade, student) -> None:
        enrollment = StudentEnrollment.objects.filter(
            student=student,
            grade=grade,
            academic_year=grade.academic_year,
            is_deleted=False,
        ).first()

        if not enrollment:
            raise ValidationError("Student is not enrolled in this grade")

        enrollment.delete()  # Soft delete via BaseSoftDeletableModel

    @staticmethod
    @transaction.atomic
    def transfer_student(student, from_grade: Grade, to_grade: Grade) -> StudentEnrollment:
        if from_grade.academic_year != to_grade.academic_year:
            raise ValidationError("Cannot transfer student between different academic years")

        # Unenroll from old grade
        AcademicYearOrchestrator.unenroll_student(from_grade, student)

        # Enroll in new grade
        return AcademicYearOrchestrator.enroll_student(to_grade, student)

    @staticmethod
    @transaction.atomic
    def bulk_enroll_students(grade: Grade, students: list) -> list[StudentEnrollment]:
        enrollments = []
        errors = []

        for student in students:
            try:
                enrollment = AcademicYearOrchestrator.enroll_student(grade, student)
                enrollments.append(enrollment)
            except ValidationError as e:
                errors.append({
                    'student': student,
                    'error': str(e),
                })

        if errors:
            # You might want to log these or handle them differently
            pass

        return enrollments

    # ========================================================================
    # SECTION 5: IMPORT TASK REPORTING (NOT DECISION-MAKING)
    # ========================================================================

    @staticmethod
    @transaction.atomic
    def create_import_task(
        academic_year: AcademicYear,
        task_type: str,
        total_records: int = 0,
        file_path: str | None = None,
    ) -> ImportTask:
        """
        Create an import task to track data import progress.
        
        This only creates the tracking record - it doesn't make decisions.
        """
        task = ImportTask.objects.create(
            academic_year=academic_year,
            task_type=task_type,
            total_records=total_records,
            file_path=file_path,
            status=ImportTask.TaskStatus.PENDING,
        )

        return task

    @staticmethod
    @transaction.atomic
    def report_import_started(import_task: ImportTask) -> None:
        import_task.status = ImportTask.TaskStatus.IN_PROGRESS
        import_task.save()

    @staticmethod
    @transaction.atomic
    def report_import_progress(
        import_task: ImportTask,
        processed: int,
        success: int,
        errors: int,
        error_details: dict | None = None,
    ) -> None:

        import_task.processed_records = processed
        import_task.success_count = success
        import_task.error_count = errors

        if error_details:
            import_task.error_details = error_details

        import_task.save()

    @staticmethod
    @transaction.atomic
    def report_import_completed(import_task: ImportTask) -> None:
        import_task.status = ImportTask.TaskStatus.COMPLETED
        import_task.completed_at = timezone.now()
        import_task.save()
        
        # Update the corresponding setup step based on task type
        setup = import_task.academic_year.setup_progress
        
        if import_task.task_type == ImportTask.TaskType.GRADES and not setup.import_grades_completed:
            # Orchestrator decides what to do when grades import completes
            AcademicYearOrchestrator.mark_step_complete(
                import_task.academic_year,
                AcademicYearSetup.SetupSteps.IMPORT_GRADES,
                import_method=AcademicYearSetup.ImportMethod.CSV,
            )
        
        elif import_task.task_type == ImportTask.TaskType.STUDENTS and not setup.import_students_completed:
            # Orchestrator decides what to do when students import completes
            AcademicYearOrchestrator.mark_step_complete(
                import_task.academic_year,
                AcademicYearSetup.SetupSteps.IMPORT_STUDENTS,
                import_method=AcademicYearSetup.ImportMethod.CSV,
            )

    @staticmethod
    @transaction.atomic
    def report_import_failed(import_task: ImportTask, error_details: dict | None = None) -> None:
        import_task.status = ImportTask.TaskStatus.FAILED
        import_task.completed_at = timezone.now()

        if error_details:
            import_task.error_details = error_details

        import_task.save()

    # ========================================================================
    # SECTION 6: QUERY HELPERS
    # ========================================================================

    @staticmethod
    def get_active_academic_year() -> AcademicYear | None:
        """Get the currently active academic year."""
        return AcademicYear.objects.filter(
            status=AcademicYear.Status.ACTIVE,
            is_deleted=False,
        ).first()

    @staticmethod
    def get_grades_for_academic_year(academic_year: AcademicYear) -> list[Grade]:
        """Get all grades for an academic year."""
        return list(Grade.objects.filter(
            academic_year=academic_year,
            is_deleted=False,
        ).order_by('grade', 'name'))

    @staticmethod
    def get_student_enrollment(student, academic_year: AcademicYear) -> StudentEnrollment | None:
        """Get a student's enrollment for a specific academic year."""
        return StudentEnrollment.objects.filter(
            student=student,
            academic_year=academic_year,
            is_deleted=False,
        ).first()

    @staticmethod
    def get_students_in_grade(grade: Grade) -> list:
        """Get all students enrolled in a grade."""
        enrollments = StudentEnrollment.objects.filter(
            grade=grade,
            is_deleted=False,
        ).select_related('student')

        return [enrollment.student for enrollment in enrollments]
