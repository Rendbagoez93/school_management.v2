"""
Tests for AcademicYearSetup and ImportTask models.

This module tests the academic year setup workflow and import task tracking.
Tests cover validation, state management, and progress tracking.
"""

import pytest
from datetime import date
from django.core.exceptions import ValidationError

from applications.school_management.academic_management.models import AcademicYear
from applications.academic_setup.models import AcademicYearSetup, ImportTask


@pytest.mark.django_db
class TestScenarioA_NewSetupStartsClean:
    """
    Scenario A: New academic year setup starts clean.
    
    Story:
    Admin creates a new academic year → setup should start at BASIC_INFO
    and not be complete.
    
    Test goals:
    - Setup exists
    - No steps completed
    - is_complete() is False
    - is_ready() is False
    """

    def test_new_setup_exists_with_default_values(self, academic_year):
        """New setup should be created with default values."""
        setup = AcademicYearSetup.objects.create(academic_year=academic_year)
        
        assert setup is not None
        assert setup.academic_year == academic_year
        assert setup.pk is not None

    def test_new_setup_starts_at_basic_info_step(self, academic_year):
        """New setup should start at BASIC_INFO step."""
        setup = AcademicYearSetup.objects.create(academic_year=academic_year)
        
        assert setup.current_step == AcademicYearSetup.SetupSteps.BASIC_INFO

    def test_new_setup_has_no_steps_completed(self, academic_year):
        """All completion flags should be False for new setup."""
        setup = AcademicYearSetup.objects.create(academic_year=academic_year)
        
        assert setup.basic_info_completed is False
        assert setup.import_grades_completed is False
        assert setup.import_students_completed is False
        assert setup.assign_classrooms_completed is False
        assert setup.review_completed is False

    def test_new_setup_has_no_import_methods(self, academic_year):
        """All import methods should be NONE for new setup."""
        setup = AcademicYearSetup.objects.create(academic_year=academic_year)
        
        assert setup.grades_import_method == AcademicYearSetup.ImportMethod.NONE
        assert setup.students_import_method == AcademicYearSetup.ImportMethod.NONE
        assert setup.classrooms_import_method == AcademicYearSetup.ImportMethod.NONE

    def test_new_setup_is_not_complete(self, academic_year):
        """is_complete() should return False for new setup."""
        setup = AcademicYearSetup.objects.create(academic_year=academic_year)
        
        assert setup.is_complete() is False

    def test_new_setup_is_not_ready(self, academic_year):
        """is_ready() should return False for new setup."""
        setup = AcademicYearSetup.objects.create(academic_year=academic_year)
        
        assert setup.is_ready() is False

    def test_one_to_one_relationship_with_academic_year(self, academic_year):
        """AcademicYearSetup should have one-to-one relationship with AcademicYear."""
        setup = AcademicYearSetup.objects.create(academic_year=academic_year)
        
        # Verify relationship from setup to academic_year
        assert setup.academic_year == academic_year
        
        # Verify reverse relationship
        assert academic_year.setup_progress == setup

    def test_cannot_create_duplicate_setup_for_same_year(self, academic_year):
        """Should not allow creating multiple setups for same academic year."""
        AcademicYearSetup.objects.create(academic_year=academic_year)
        
        # Attempting to create another setup for the same year should fail
        with pytest.raises(Exception):  # Django will raise IntegrityError
            AcademicYearSetup.objects.create(academic_year=academic_year)


@pytest.mark.django_db
class TestScenarioB_GradesMarkedCompletedWithoutMethod:
    """
    Scenario B: Grades marked completed without import method → rejected.
    
    Story:
    Admin clicks "Grades imported" but didn't specify how → system must block it.
    
    This validates the clean() method.
    """

    def test_grades_completed_without_method_fails_validation(self, academic_year):
        """Setting grades completed without import method should raise ValidationError."""
        setup = AcademicYearSetup.objects.create(academic_year=academic_year)
        
        # Mark grades as completed without setting import method
        setup.import_grades_completed = True
        setup.grades_import_method = AcademicYearSetup.ImportMethod.NONE
        
        with pytest.raises(ValidationError) as exc_info:
            setup.full_clean()
        
        assert "grades_import_method" in exc_info.value.message_dict
        assert "Import method must be specified" in str(exc_info.value)

    def test_students_completed_without_method_fails_validation(self, academic_year):
        """Setting students completed without import method should raise ValidationError."""
        setup = AcademicYearSetup.objects.create(academic_year=academic_year)
        
        # Mark students as completed without setting import method
        setup.import_students_completed = True
        setup.students_import_method = AcademicYearSetup.ImportMethod.NONE
        
        with pytest.raises(ValidationError) as exc_info:
            setup.full_clean()
        
        assert "students_import_method" in exc_info.value.message_dict
        assert "Import method must be specified" in str(exc_info.value)

    def test_classrooms_completed_without_method_fails_validation(self, academic_year):
        """Setting classrooms completed without import method should raise ValidationError."""
        setup = AcademicYearSetup.objects.create(academic_year=academic_year)
        
        # Mark classrooms as completed without setting import method
        setup.assign_classrooms_completed = True
        setup.classrooms_import_method = AcademicYearSetup.ImportMethod.NONE
        
        with pytest.raises(ValidationError) as exc_info:
            setup.full_clean()
        
        assert "classrooms_import_method" in exc_info.value.message_dict
        assert "Import method must be specified" in str(exc_info.value)

    def test_multiple_steps_completed_without_methods_shows_all_errors(self, academic_year):
        """Multiple validation errors should all be reported."""
        setup = AcademicYearSetup.objects.create(academic_year=academic_year)
        
        # Mark multiple steps as completed without import methods
        setup.import_grades_completed = True
        setup.import_students_completed = True
        setup.grades_import_method = AcademicYearSetup.ImportMethod.NONE
        setup.students_import_method = AcademicYearSetup.ImportMethod.NONE
        
        with pytest.raises(ValidationError) as exc_info:
            setup.full_clean()
        
        errors = exc_info.value.message_dict
        assert "grades_import_method" in errors
        assert "students_import_method" in errors


@pytest.mark.django_db
class TestScenarioC_ProperGradeImportPassesValidation:
    """
    Scenario C: Proper grade import passes validation.
    
    Story:
    Admin imports grades via CSV → marks step completed → system accepts it.
    """

    def test_grades_import_via_csv_passes_validation(self, academic_year):
        """Setting grades completed with CSV method should pass validation."""
        setup = AcademicYearSetup.objects.create(academic_year=academic_year)
        
        # Mark grades as completed with CSV method
        setup.import_grades_completed = True
        setup.grades_import_method = AcademicYearSetup.ImportMethod.CSV
        
        # Should not raise ValidationError
        setup.full_clean()
        setup.save()
        
        # Verify it was saved correctly
        setup.refresh_from_db()
        assert setup.import_grades_completed is True
        assert setup.grades_import_method == AcademicYearSetup.ImportMethod.CSV

    def test_grades_import_via_manual_passes_validation(self, academic_year):
        """Setting grades completed with MANUAL method should pass validation."""
        setup = AcademicYearSetup.objects.create(academic_year=academic_year)
        
        setup.import_grades_completed = True
        setup.grades_import_method = AcademicYearSetup.ImportMethod.MANUAL
        
        setup.full_clean()
        setup.save()
        
        setup.refresh_from_db()
        assert setup.import_grades_completed is True
        assert setup.grades_import_method == AcademicYearSetup.ImportMethod.MANUAL

    def test_grades_import_via_api_passes_validation(self, academic_year):
        """Setting grades completed with API method should pass validation."""
        setup = AcademicYearSetup.objects.create(academic_year=academic_year)
        
        setup.import_grades_completed = True
        setup.grades_import_method = AcademicYearSetup.ImportMethod.API
        
        setup.full_clean()
        setup.save()
        
        setup.refresh_from_db()
        assert setup.import_grades_completed is True
        assert setup.grades_import_method == AcademicYearSetup.ImportMethod.API

    def test_all_import_methods_valid_together(self, academic_year):
        """All steps can be completed with different import methods."""
        setup = AcademicYearSetup.objects.create(academic_year=academic_year)
        
        # Complete all import steps with different methods
        setup.import_grades_completed = True
        setup.import_students_completed = True
        setup.assign_classrooms_completed = True
        setup.grades_import_method = AcademicYearSetup.ImportMethod.CSV
        setup.students_import_method = AcademicYearSetup.ImportMethod.API
        setup.classrooms_import_method = AcademicYearSetup.ImportMethod.MANUAL
        
        setup.full_clean()
        setup.save()
        
        setup.refresh_from_db()
        assert setup.import_grades_completed is True
        assert setup.import_students_completed is True
        assert setup.assign_classrooms_completed is True

    def test_can_have_import_method_without_completion(self, academic_year):
        """Can set import method before marking as completed (planning)."""
        setup = AcademicYearSetup.objects.create(academic_year=academic_year)
        
        # Set method but not completed (admin is planning to use CSV)
        setup.import_grades_completed = False
        setup.grades_import_method = AcademicYearSetup.ImportMethod.CSV
        
        # Should pass validation
        setup.full_clean()
        setup.save()
        
        setup.refresh_from_db()
        assert setup.import_grades_completed is False
        assert setup.grades_import_method == AcademicYearSetup.ImportMethod.CSV


@pytest.mark.django_db
class TestScenarioD_FullSetupCompleted:
    """
    Scenario D: Full setup completed → academic year ready.
    
    Story:
    Admin finishes all steps → academic year becomes usable.
    """

    def test_all_steps_completed_makes_setup_complete(self, academic_year):
        """is_complete() returns True when all steps are completed."""
        setup = AcademicYearSetup.objects.create(
            academic_year=academic_year,
            basic_info_completed=True,
            import_grades_completed=True,
            import_students_completed=True,
            assign_classrooms_completed=True,
            review_completed=True,
            grades_import_method=AcademicYearSetup.ImportMethod.CSV,
            students_import_method=AcademicYearSetup.ImportMethod.CSV,
            classrooms_import_method=AcademicYearSetup.ImportMethod.MANUAL,
        )
        
        assert setup.is_complete() is True

    def test_all_steps_completed_makes_setup_ready(self, academic_year):
        """is_ready() returns True when all steps are completed."""
        setup = AcademicYearSetup.objects.create(
            academic_year=academic_year,
            basic_info_completed=True,
            import_grades_completed=True,
            import_students_completed=True,
            assign_classrooms_completed=True,
            review_completed=True,
            grades_import_method=AcademicYearSetup.ImportMethod.CSV,
            students_import_method=AcademicYearSetup.ImportMethod.CSV,
            classrooms_import_method=AcademicYearSetup.ImportMethod.MANUAL,
        )
        
        assert setup.is_ready() is True

    def test_missing_one_step_means_not_complete(self, academic_year):
        """Missing any single step means setup is not complete."""
        # Missing review_completed
        setup = AcademicYearSetup.objects.create(
            academic_year=academic_year,
            basic_info_completed=True,
            import_grades_completed=True,
            import_students_completed=True,
            assign_classrooms_completed=True,
            review_completed=False,  # Missing this
            grades_import_method=AcademicYearSetup.ImportMethod.CSV,
            students_import_method=AcademicYearSetup.ImportMethod.CSV,
            classrooms_import_method=AcademicYearSetup.ImportMethod.MANUAL,
        )
        
        assert setup.is_complete() is False
        assert setup.is_ready() is False

    def test_each_missing_step_individually_means_not_complete(self, academic_year):
        """Test that each step is required for completion."""
        base_data = {
            "academic_year": academic_year,
            "basic_info_completed": True,
            "import_grades_completed": True,
            "import_students_completed": True,
            "assign_classrooms_completed": True,
            "review_completed": True,
            "grades_import_method": AcademicYearSetup.ImportMethod.CSV,
            "students_import_method": AcademicYearSetup.ImportMethod.CSV,
            "classrooms_import_method": AcademicYearSetup.ImportMethod.MANUAL,
        }
        
        # Test each step individually
        steps_to_test = [
            "basic_info_completed",
            "import_grades_completed",
            "import_students_completed",
            "assign_classrooms_completed",
            "review_completed",
        ]
        
        for step in steps_to_test:
            data = base_data.copy()
            data[step] = False
            
            # Create new academic year for each test to avoid conflicts
            year = AcademicYear.objects.create(
                name=f"Test-{step}",
                start_date=date(2025, 9, 1),
                end_date=date(2026, 6, 30),
            )
            data["academic_year"] = year
            
            setup = AcademicYearSetup.objects.create(**data)
            
            assert setup.is_complete() is False, f"Setup should not be complete when {step} is False"
            assert setup.is_ready() is False, f"Setup should not be ready when {step} is False"

    def test_fully_completed_setup_fixture(self, fully_completed_setup):
        """Test the fully_completed_setup fixture works correctly."""
        assert fully_completed_setup.is_complete() is True
        assert fully_completed_setup.is_ready() is True
        assert fully_completed_setup.current_step == AcademicYearSetup.SetupSteps.COMPLETED


@pytest.mark.django_db
class TestScenarioE_NewImportTaskStartsAtZeroPercent:
    """
    Scenario E: New import task starts at 0%.
    
    Story:
    Admin uploads CSV → task is created → nothing processed yet.
    """

    def test_new_import_task_has_zero_records(self, academic_year):
        """New import task should start with 0 total and processed records."""
        task = ImportTask.objects.create(
            academic_year=academic_year,
            task_type=ImportTask.TaskType.STUDENTS,
        )
        
        assert task.total_records == 0
        assert task.processed_records == 0

    def test_new_import_task_has_zero_counts(self, academic_year):
        """New import task should have 0 success and error counts."""
        task = ImportTask.objects.create(
            academic_year=academic_year,
            task_type=ImportTask.TaskType.GRADES,
        )
        
        assert task.success_count == 0
        assert task.error_count == 0

    def test_new_import_task_has_pending_status(self, academic_year):
        """New import task should have PENDING status by default."""
        task = ImportTask.objects.create(
            academic_year=academic_year,
            task_type=ImportTask.TaskType.CLASSROOMS,
        )
        
        assert task.status == ImportTask.TaskStatus.PENDING

    def test_new_import_task_progress_is_zero(self, academic_year):
        """New import task should have 0% progress."""
        task = ImportTask.objects.create(
            academic_year=academic_year,
            task_type=ImportTask.TaskType.STUDENTS,
        )
        
        assert task.progress_percentage == 0

    def test_import_task_with_file_path(self, academic_year):
        """Import task can be created with file path."""
        task = ImportTask.objects.create(
            academic_year=academic_year,
            task_type=ImportTask.TaskType.STUDENTS,
            file_path="/uploads/students_2025.csv",
        )
        
        assert task.file_path == "/uploads/students_2025.csv"
        assert task.progress_percentage == 0

    def test_import_task_fixture(self, import_task_pending):
        """Test the import_task_pending fixture."""
        assert import_task_pending.status == ImportTask.TaskStatus.PENDING
        assert import_task_pending.total_records == 0
        assert import_task_pending.processed_records == 0
        assert import_task_pending.progress_percentage == 0


@pytest.mark.django_db
class TestScenarioF_ImportProgressUpdatesCorrectly:
    """
    Scenario F: Import progress updates correctly.
    
    Story:
    System processed 25 out of 100 students → progress is 25%.
    """

    def test_progress_25_percent_with_25_of_100(self, academic_year):
        """Processing 25 out of 100 records should show 25% progress."""
        task = ImportTask.objects.create(
            academic_year=academic_year,
            task_type=ImportTask.TaskType.STUDENTS,
            total_records=100,
            processed_records=25,
        )
        
        assert task.progress_percentage == 25.0

    def test_progress_50_percent_with_50_of_100(self, academic_year):
        """Processing 50 out of 100 records should show 50% progress."""
        task = ImportTask.objects.create(
            academic_year=academic_year,
            task_type=ImportTask.TaskType.GRADES,
            total_records=100,
            processed_records=50,
        )
        
        assert task.progress_percentage == 50.0

    def test_progress_100_percent_when_complete(self, academic_year):
        """Processing all records should show 100% progress."""
        task = ImportTask.objects.create(
            academic_year=academic_year,
            task_type=ImportTask.TaskType.CLASSROOMS,
            total_records=200,
            processed_records=200,
        )
        
        assert task.progress_percentage == 100.0

    def test_progress_updates_as_records_processed(self, academic_year):
        """Progress should update correctly as more records are processed."""
        task = ImportTask.objects.create(
            academic_year=academic_year,
            task_type=ImportTask.TaskType.STUDENTS,
            total_records=100,
            processed_records=0,
        )
        
        assert task.progress_percentage == 0.0
        
        # Process 10 records
        task.processed_records = 10
        task.save()
        assert task.progress_percentage == 10.0
        
        # Process 25 more (35 total)
        task.processed_records = 35
        task.save()
        assert task.progress_percentage == 35.0
        
        # Process remaining (100 total)
        task.processed_records = 100
        task.save()
        assert task.progress_percentage == 100.0

    def test_progress_with_non_round_numbers(self, academic_year):
        """Progress should calculate correctly with non-round percentages."""
        task = ImportTask.objects.create(
            academic_year=academic_year,
            task_type=ImportTask.TaskType.STUDENTS,
            total_records=7,
            processed_records=3,
        )
        
        # 3/7 = ~42.857%
        expected = (3 / 7) * 100
        assert abs(task.progress_percentage - expected) < 0.01

    def test_fixture_import_task_in_progress(self, import_task_in_progress):
        """Test the import_task_in_progress fixture."""
        assert import_task_in_progress.total_records == 100
        assert import_task_in_progress.processed_records == 25
        assert import_task_in_progress.progress_percentage == 25.0
        assert import_task_in_progress.status == ImportTask.TaskStatus.IN_PROGRESS


@pytest.mark.django_db
class TestScenarioG_NoRecordsAvoidDivisionErrors:
    """
    Scenario G: No records → avoid division errors.
    
    Story:
    Import task created but no rows detected → progress should be 0%, not crash.
    """

    def test_zero_total_records_returns_zero_progress(self, academic_year):
        """Progress should be 0% when total_records is 0, not raise ZeroDivisionError."""
        task = ImportTask.objects.create(
            academic_year=academic_year,
            task_type=ImportTask.TaskType.STUDENTS,
            total_records=0,
            processed_records=0,
        )
        
        # Should not raise ZeroDivisionError
        assert task.progress_percentage == 0

    def test_empty_csv_file_scenario(self, academic_year):
        """Simulates uploading an empty CSV file."""
        task = ImportTask.objects.create(
            academic_year=academic_year,
            task_type=ImportTask.TaskType.GRADES,
            file_path="/uploads/empty.csv",
            total_records=0,
            processed_records=0,
            status=ImportTask.TaskStatus.COMPLETED,
        )
        
        assert task.progress_percentage == 0
        assert task.status == ImportTask.TaskStatus.COMPLETED

    def test_failed_file_read_scenario(self, academic_year):
        """Simulates a failed file read where no records were detected."""
        task = ImportTask.objects.create(
            academic_year=academic_year,
            task_type=ImportTask.TaskType.STUDENTS,
            file_path="/uploads/corrupted.csv",
            total_records=0,
            processed_records=0,
            status=ImportTask.TaskStatus.FAILED,
            error_details={"error": "File could not be read"},
        )
        
        assert task.progress_percentage == 0
        assert task.status == ImportTask.TaskStatus.FAILED

    def test_progress_remains_zero_throughout_empty_task(self, academic_year):
        """Progress should remain 0% even as task status changes."""
        task = ImportTask.objects.create(
            academic_year=academic_year,
            task_type=ImportTask.TaskType.CLASSROOMS,
            total_records=0,
        )
        
        # Initially pending
        assert task.progress_percentage == 0
        
        # Change to in progress
        task.status = ImportTask.TaskStatus.IN_PROGRESS
        task.save()
        assert task.progress_percentage == 0
        
        # Change to completed
        task.status = ImportTask.TaskStatus.COMPLETED
        task.save()
        assert task.progress_percentage == 0

    def test_multiple_tasks_with_zero_records(self, academic_year):
        """Multiple tasks with 0 records should all return 0% progress."""
        tasks = [
            ImportTask.objects.create(
                academic_year=academic_year,
                task_type=task_type,
                total_records=0,
            )
            for task_type in [
                ImportTask.TaskType.GRADES,
                ImportTask.TaskType.STUDENTS,
                ImportTask.TaskType.CLASSROOMS,
            ]
        ]
        
        for task in tasks:
            assert task.progress_percentage == 0


@pytest.mark.django_db
class TestAdditionalModelBehavior:
    """Additional tests for model behavior and edge cases."""

    def test_academic_year_setup_string_representation(self, academic_year):
        """Test __str__ method of AcademicYearSetup."""
        setup = AcademicYearSetup.objects.create(academic_year=academic_year)
        
        expected = f"Setup for {academic_year.name}"
        assert str(setup) == expected

    def test_import_task_string_representation(self, academic_year):
        """Test __str__ method of ImportTask."""
        task = ImportTask.objects.create(
            academic_year=academic_year,
            task_type=ImportTask.TaskType.STUDENTS,
        )
        
        expected = f"Students import for {academic_year.name}"
        assert str(task) == expected

    def test_multiple_import_tasks_for_same_academic_year(self, academic_year):
        """Multiple import tasks can exist for the same academic year."""
        task1 = ImportTask.objects.create(
            academic_year=academic_year,
            task_type=ImportTask.TaskType.GRADES,
        )
        task2 = ImportTask.objects.create(
            academic_year=academic_year,
            task_type=ImportTask.TaskType.STUDENTS,
        )
        task3 = ImportTask.objects.create(
            academic_year=academic_year,
            task_type=ImportTask.TaskType.CLASSROOMS,
        )
        
        assert ImportTask.objects.filter(academic_year=academic_year).count() == 3
        assert task1.academic_year == task2.academic_year == task3.academic_year

    def test_import_task_error_details_json(self, academic_year):
        """Import task can store complex error details as JSON."""
        error_data = {
            "file": "students.csv",
            "errors": [
                {"row": 1, "field": "email", "message": "Invalid format"},
                {"row": 3, "field": "grade", "message": "Grade not found"},
            ],
            "summary": "2 errors found",
        }
        
        task = ImportTask.objects.create(
            academic_year=academic_year,
            task_type=ImportTask.TaskType.STUDENTS,
            status=ImportTask.TaskStatus.FAILED,
            error_details=error_data,
        )
        
        task.refresh_from_db()
        assert task.error_details == error_data
        assert len(task.error_details["errors"]) == 2

    def test_setup_with_all_import_methods(self, academic_year):
        """Test all available import method choices."""
        setup = AcademicYearSetup.objects.create(academic_year=academic_year)
        
        methods = [
            AcademicYearSetup.ImportMethod.NONE,
            AcademicYearSetup.ImportMethod.MANUAL,
            AcademicYearSetup.ImportMethod.CSV,
            AcademicYearSetup.ImportMethod.API,
        ]
        
        for method in methods:
            setup.grades_import_method = method
            setup.save()
            setup.refresh_from_db()
            assert setup.grades_import_method == method

    def test_import_task_all_statuses(self, academic_year):
        """Test all available task status choices."""
        statuses = [
            ImportTask.TaskStatus.PENDING,
            ImportTask.TaskStatus.IN_PROGRESS,
            ImportTask.TaskStatus.COMPLETED,
            ImportTask.TaskStatus.FAILED,
        ]
        
        for status in statuses:
            task = ImportTask.objects.create(
                academic_year=academic_year,
                task_type=ImportTask.TaskType.STUDENTS,
                status=status,
            )
            assert task.status == status

    def test_import_task_all_types(self, academic_year):
        """Test all available task type choices."""
        types = [
            ImportTask.TaskType.GRADES,
            ImportTask.TaskType.STUDENTS,
            ImportTask.TaskType.CLASSROOMS,
        ]
        
        for task_type in types:
            task = ImportTask.objects.create(
                academic_year=academic_year,
                task_type=task_type,
            )
            assert task.task_type == task_type
