"""
Test Scenario 3: Grades Imported via CSV

Real-World Flow:
✔ Admin uploads CSV
✔ System creates ImportTask
✔ Progress updates
✔ Errors logged
✔ On success: step advances
"""

import pytest
from applications.academic_setup.models import AcademicYearSetup, ImportTask
from applications.academic_setup.orchestrator import AcademicYearOrchestrator


@pytest.mark.django_db
class TestCSVImportInitiation:
    """Test CSV import task creation."""
    
    def test_create_grades_import_task(self, fresh_start_academic_year):
        """Verify creating a grades import task."""
        task = AcademicYearOrchestrator.create_import_task(
            academic_year=fresh_start_academic_year,
            task_type=ImportTask.TaskType.GRADES,
            total_records=100,
            file_path="/uploads/grades.csv",
        )
        
        assert task.id is not None
        assert task.academic_year == fresh_start_academic_year
        assert task.task_type == ImportTask.TaskType.GRADES
        assert task.total_records == 100
        assert task.file_path == "/uploads/grades.csv"
    
    def test_new_import_task_has_pending_status(self, fresh_start_academic_year):
        """Verify new import task starts with PENDING status."""
        task = AcademicYearOrchestrator.create_import_task(
            academic_year=fresh_start_academic_year,
            task_type=ImportTask.TaskType.GRADES,
            total_records=50,
        )
        
        assert task.status == ImportTask.TaskStatus.PENDING
    
    def test_new_import_task_has_zero_progress(self, fresh_start_academic_year):
        """Verify new import task has zero progress."""
        task = AcademicYearOrchestrator.create_import_task(
            academic_year=fresh_start_academic_year,
            task_type=ImportTask.TaskType.STUDENTS,
            total_records=200,
        )
        
        assert task.processed_records == 0
        assert task.success_count == 0
        assert task.error_count == 0
        assert task.progress_percentage == 0.0
    
    def test_import_task_created_via_fixture(self, pending_grades_import_task):
        """Test using the pending_grades_import_task fixture."""
        assert pending_grades_import_task.status == ImportTask.TaskStatus.PENDING
        assert pending_grades_import_task.task_type == ImportTask.TaskType.GRADES
        assert pending_grades_import_task.total_records == 100


@pytest.mark.django_db
class TestCSVImportProgressTracking:
    """Test import progress updates."""
    
    def test_start_import_task(self, pending_grades_import_task):
        """Verify starting an import task updates status."""
        AcademicYearOrchestrator.report_import_started(pending_grades_import_task)
        
        pending_grades_import_task.refresh_from_db()
        assert pending_grades_import_task.status == ImportTask.TaskStatus.IN_PROGRESS
    
    def test_update_import_progress(self, pending_grades_import_task):
        """Verify updating import progress."""
        AcademicYearOrchestrator.report_import_started(pending_grades_import_task)
        
        AcademicYearOrchestrator.report_import_progress(
            pending_grades_import_task,
            processed=50,
            success=48,
            errors=2,
        )
        
        pending_grades_import_task.refresh_from_db()
        
        assert pending_grades_import_task.processed_records == 50
        assert pending_grades_import_task.success_count == 48
        assert pending_grades_import_task.error_count == 2
        assert pending_grades_import_task.progress_percentage == 50.0
    
    def test_progress_percentage_calculation(self, pending_grades_import_task):
        """Verify progress percentage is calculated correctly."""
        AcademicYearOrchestrator.report_import_started(pending_grades_import_task)
        
        # 25% progress
        AcademicYearOrchestrator.report_import_progress(
            pending_grades_import_task,
            processed=25,
            success=25,
            errors=0,
        )
        pending_grades_import_task.refresh_from_db()
        assert pending_grades_import_task.progress_percentage == 25.0
        
        # 75% progress
        AcademicYearOrchestrator.report_import_progress(
            pending_grades_import_task,
            processed=75,
            success=73,
            errors=2,
        )
        pending_grades_import_task.refresh_from_db()
        assert pending_grades_import_task.progress_percentage == 75.0
        
        # 100% progress
        AcademicYearOrchestrator.report_import_progress(
            pending_grades_import_task,
            processed=100,
            success=98,
            errors=2,
        )
        pending_grades_import_task.refresh_from_db()
        assert pending_grades_import_task.progress_percentage == 100.0
    
    def test_log_import_errors(self, pending_grades_import_task):
        """Verify errors are logged during import."""
        AcademicYearOrchestrator.report_import_started(pending_grades_import_task)
        
        error_details = {
            "errors": [
                {"row": 5, "error": "Invalid grade format"},
                {"row": 12, "error": "Duplicate grade name"},
            ]
        }
        
        AcademicYearOrchestrator.report_import_progress(
            pending_grades_import_task,
            processed=20,
            success=18,
            errors=2,
            error_details=error_details,
        )
        
        pending_grades_import_task.refresh_from_db()
        
        assert pending_grades_import_task.error_count == 2
        assert pending_grades_import_task.error_details == error_details


@pytest.mark.django_db
class TestCSVImportCompletion:
    """Test successful import completion."""
    
    def test_complete_grades_import(self, pending_grades_import_task):
        """Verify completing a grades import task."""
        # Start import
        AcademicYearOrchestrator.report_import_started(pending_grades_import_task)
        
        # Update progress to completion
        AcademicYearOrchestrator.report_import_progress(
            pending_grades_import_task,
            processed=100,
            success=100,
            errors=0,
        )
        
        # Mark as completed
        AcademicYearOrchestrator.report_import_completed(pending_grades_import_task)
        
        pending_grades_import_task.refresh_from_db()
        
        assert pending_grades_import_task.status == ImportTask.TaskStatus.COMPLETED
        assert pending_grades_import_task.completed_at is not None
    
    def test_grades_import_completion_advances_setup_step(self, fresh_start_academic_year):
        """Verify grades import completion advances setup step."""
        # Complete basic info first
        AcademicYearOrchestrator.mark_step_complete(
            fresh_start_academic_year,
            AcademicYearSetup.SetupSteps.BASIC_INFO,
        )
        
        # Create and complete grades import
        task = AcademicYearOrchestrator.create_import_task(
            academic_year=fresh_start_academic_year,
            task_type=ImportTask.TaskType.GRADES,
            total_records=50,
        )
        
        AcademicYearOrchestrator.report_import_started(task)
        AcademicYearOrchestrator.report_import_progress(task, 50, 50, 0)
        AcademicYearOrchestrator.report_import_completed(task)
        
        # Verify setup progressed
        setup = fresh_start_academic_year.setup_progress
        setup.refresh_from_db()
        
        assert setup.import_grades_completed is True
        assert setup.grades_import_method == AcademicYearSetup.ImportMethod.CSV
        assert setup.current_step == AcademicYearSetup.SetupSteps.IMPORT_STUDENTS
    
    def test_students_import_completion_advances_setup_step(self, grades_imported_setup):
        """Verify students import completion advances setup step."""
        academic_year = grades_imported_setup.academic_year
        
        # Create and complete students import
        task = AcademicYearOrchestrator.create_import_task(
            academic_year=academic_year,
            task_type=ImportTask.TaskType.STUDENTS,
            total_records=200,
        )
        
        AcademicYearOrchestrator.report_import_started(task)
        AcademicYearOrchestrator.report_import_progress(task, 200, 200, 0)
        AcademicYearOrchestrator.report_import_completed(task)
        
        # Verify setup progressed
        grades_imported_setup.refresh_from_db()
        
        assert grades_imported_setup.import_students_completed is True
        assert grades_imported_setup.students_import_method == AcademicYearSetup.ImportMethod.CSV
        assert grades_imported_setup.current_step == AcademicYearSetup.SetupSteps.ASSIGN_CLASSROOMS


@pytest.mark.django_db
class TestMultipleImportTasks:
    """Test multiple import tasks for same academic year."""
    
    def test_multiple_import_tasks_for_different_types(self, fresh_start_academic_year):
        """Verify can have multiple import tasks for different types."""
        grades_task = AcademicYearOrchestrator.create_import_task(
            academic_year=fresh_start_academic_year,
            task_type=ImportTask.TaskType.GRADES,
            total_records=50,
        )
        
        students_task = AcademicYearOrchestrator.create_import_task(
            academic_year=fresh_start_academic_year,
            task_type=ImportTask.TaskType.STUDENTS,
            total_records=200,
        )
        
        classrooms_task = AcademicYearOrchestrator.create_import_task(
            academic_year=fresh_start_academic_year,
            task_type=ImportTask.TaskType.CLASSROOMS,
            total_records=10,
        )
        
        # All tasks should exist
        tasks = ImportTask.objects.filter(academic_year=fresh_start_academic_year)
        assert tasks.count() == 3
        
        # Verify different types
        task_types = set(tasks.values_list('task_type', flat=True))
        assert task_types == {
            ImportTask.TaskType.GRADES,
            ImportTask.TaskType.STUDENTS,
            ImportTask.TaskType.CLASSROOMS,
        }
    
    def test_can_track_multiple_tasks_independently(self, fresh_start_academic_year):
        """Verify multiple tasks can have independent progress."""
        task1 = AcademicYearOrchestrator.create_import_task(
            academic_year=fresh_start_academic_year,
            task_type=ImportTask.TaskType.GRADES,
            total_records=100,
        )
        
        task2 = AcademicYearOrchestrator.create_import_task(
            academic_year=fresh_start_academic_year,
            task_type=ImportTask.TaskType.STUDENTS,
            total_records=200,
        )
        
        # Update task1
        AcademicYearOrchestrator.report_import_started(task1)
        AcademicYearOrchestrator.report_import_progress(task1, 50, 50, 0)
        
        # Update task2
        AcademicYearOrchestrator.report_import_started(task2)
        AcademicYearOrchestrator.report_import_progress(task2, 100, 95, 5)
        
        # Verify independent progress
        task1.refresh_from_db()
        task2.refresh_from_db()
        
        assert task1.processed_records == 50
        assert task1.progress_percentage == 50.0
        
        assert task2.processed_records == 100
        assert task2.progress_percentage == 50.0


@pytest.mark.django_db
class TestCSVImportWithGradeCreation:
    """Test CSV import that creates actual grades."""
    
    def test_import_creates_grades(self, fresh_start_academic_year, csv_grades_data):
        """Verify import can create grades in the system."""
        # Import grades using orchestrator
        grades = AcademicYearOrchestrator.bulk_create_grades(
            fresh_start_academic_year,
            csv_grades_data
        )
        
        assert len(grades) == len(csv_grades_data)
        
        # Verify grades are created
        db_grades = fresh_start_academic_year.grades.filter(is_deleted=False)
        assert db_grades.count() == len(csv_grades_data)
    
    def test_import_task_tracks_grade_creation(self, fresh_start_academic_year, csv_grades_data):
        """Verify import task accurately tracks grade creation."""
        # Create import task
        task = AcademicYearOrchestrator.create_import_task(
            academic_year=fresh_start_academic_year,
            task_type=ImportTask.TaskType.GRADES,
            total_records=len(csv_grades_data),
            file_path="/uploads/grades.csv",
        )
        
        # Start import
        AcademicYearOrchestrator.report_import_started(task)
        
        # Create grades
        grades = AcademicYearOrchestrator.bulk_create_grades(
            fresh_start_academic_year,
            csv_grades_data
        )
        
        # Report progress
        AcademicYearOrchestrator.report_import_progress(
            task,
            processed=len(grades),
            success=len(grades),
            errors=0,
        )
        
        # Complete import
        AcademicYearOrchestrator.report_import_completed(task)
        
        task.refresh_from_db()
        
        assert task.status == ImportTask.TaskStatus.COMPLETED
        assert task.success_count == len(csv_grades_data)
        assert task.error_count == 0
        assert task.progress_percentage == 100.0
