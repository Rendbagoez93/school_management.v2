"""
Test Scenario 7: Retry Failed Import

Realistic Behavior:
✔ Admin retries failed CSV
✔ New ImportTask created
✔ Old task preserved (audit trail)
✔ Both tasks visible in history
✔ Can identify which attempt succeeded
"""

import pytest
from applications.academic_setup.models import AcademicYearSetup, ImportTask
from applications.academic_setup.orchestrator import AcademicYearOrchestrator


@pytest.mark.django_db
class TestRetryFailedImport:
    """Test retrying failed imports."""
    
    def test_retry_creates_new_import_task(self, failed_import_task):
        """Verify retrying creates a new import task."""
        academic_year = failed_import_task.academic_year
        original_task_id = failed_import_task.id
        
        # Admin retries the import with corrected file
        retry_task = AcademicYearOrchestrator.create_import_task(
            academic_year=academic_year,
            task_type=failed_import_task.task_type,
            total_records=100,
            file_path="/uploads/students_corrected.csv",
        )
        
        # Verify new task created
        assert retry_task.id != original_task_id
        assert retry_task.status == ImportTask.TaskStatus.PENDING
        assert retry_task.task_type == failed_import_task.task_type
    
    def test_old_failed_task_preserved(self, failed_import_task):
        """Verify old failed task is preserved as audit trail."""
        academic_year = failed_import_task.academic_year
        
        # Create retry task
        retry_task = AcademicYearOrchestrator.create_import_task(
            academic_year=academic_year,
            task_type=failed_import_task.task_type,
            total_records=100,
        )
        
        # Verify old task still exists
        failed_import_task.refresh_from_db()
        assert failed_import_task.status == ImportTask.TaskStatus.FAILED
        assert failed_import_task.completed_at is not None
        
        # Both tasks should be queryable
        all_tasks = ImportTask.objects.filter(
            academic_year=academic_year,
            task_type=failed_import_task.task_type
        )
        assert all_tasks.count() == 2
    
    def test_retry_can_succeed_where_original_failed(self, failed_import_task):
        """Verify retry can succeed where original failed."""
        academic_year = failed_import_task.academic_year
        
        # Create and complete retry task successfully
        retry_task = AcademicYearOrchestrator.create_import_task(
            academic_year=academic_year,
            task_type=failed_import_task.task_type,
            total_records=100,
            file_path="/uploads/students_corrected.csv",
        )
        
        AcademicYearOrchestrator.report_import_started(retry_task)
        AcademicYearOrchestrator.report_import_progress(
            retry_task, processed=100, success=100, errors=0
        )
        AcademicYearOrchestrator.report_import_completed(retry_task)
        
        retry_task.refresh_from_db()
        
        # Verify retry succeeded
        assert retry_task.status == ImportTask.TaskStatus.COMPLETED
        assert retry_task.success_count == 100
        assert retry_task.error_count == 0
        
        # Original still failed
        failed_import_task.refresh_from_db()
        assert failed_import_task.status == ImportTask.TaskStatus.FAILED


@pytest.mark.django_db
class TestMultipleRetryAttempts:
    """Test multiple retry attempts."""
    
    def test_multiple_retry_attempts_all_preserved(self, fresh_start_academic_year):
        """Verify multiple retry attempts are all preserved."""
        # First attempt - fails
        task1 = AcademicYearOrchestrator.create_import_task(
            academic_year=fresh_start_academic_year,
            task_type=ImportTask.TaskType.STUDENTS,
            total_records=100,
            file_path="/uploads/attempt1.csv",
        )
        AcademicYearOrchestrator.report_import_started(task1)
        AcademicYearOrchestrator.report_import_failed(
            task1,
            error_details={"error": "Attempt 1 failed"}
        )
        
        # Second attempt - also fails
        task2 = AcademicYearOrchestrator.create_import_task(
            academic_year=fresh_start_academic_year,
            task_type=ImportTask.TaskType.STUDENTS,
            total_records=100,
            file_path="/uploads/attempt2.csv",
        )
        AcademicYearOrchestrator.report_import_started(task2)
        AcademicYearOrchestrator.report_import_failed(
            task2,
            error_details={"error": "Attempt 2 failed"}
        )
        
        # Third attempt - succeeds
        task3 = AcademicYearOrchestrator.create_import_task(
            academic_year=fresh_start_academic_year,
            task_type=ImportTask.TaskType.STUDENTS,
            total_records=100,
            file_path="/uploads/attempt3.csv",
        )
        AcademicYearOrchestrator.report_import_started(task3)
        AcademicYearOrchestrator.report_import_progress(
            task3, processed=100, success=100, errors=0
        )
        AcademicYearOrchestrator.report_import_completed(task3)
        
        # Verify all three tasks exist
        all_tasks = ImportTask.objects.filter(
            academic_year=fresh_start_academic_year,
            task_type=ImportTask.TaskType.STUDENTS
        ).order_by('created_at')
        
        assert all_tasks.count() == 3
        
        # Verify states
        tasks = list(all_tasks)
        assert tasks[0].status == ImportTask.TaskStatus.FAILED
        assert tasks[1].status == ImportTask.TaskStatus.FAILED
        assert tasks[2].status == ImportTask.TaskStatus.COMPLETED
    
    def test_can_identify_successful_attempt(self, fresh_start_academic_year):
        """Verify can identify which retry attempt succeeded."""
        # Create multiple attempts
        for i in range(3):
            task = AcademicYearOrchestrator.create_import_task(
                academic_year=fresh_start_academic_year,
                task_type=ImportTask.TaskType.GRADES,
                total_records=50,
                file_path=f"/uploads/attempt{i+1}.csv",
            )
            AcademicYearOrchestrator.report_import_started(task)
            
            if i < 2:
                # First two fail
                AcademicYearOrchestrator.report_import_failed(task)
            else:
                # Third succeeds
                AcademicYearOrchestrator.report_import_progress(
                    task, processed=50, success=50, errors=0
                )
                AcademicYearOrchestrator.report_import_completed(task)
        
        # Query for successful task
        successful_task = ImportTask.objects.filter(
            academic_year=fresh_start_academic_year,
            task_type=ImportTask.TaskType.GRADES,
            status=ImportTask.TaskStatus.COMPLETED
        ).first()
        
        assert successful_task is not None
        assert successful_task.file_path == "/uploads/attempt3.csv"


@pytest.mark.django_db
class TestAuditTrailForRetries:
    """Test audit trail functionality for retries."""
    
    def test_all_attempts_have_timestamps(self, fresh_start_academic_year):
        """Verify all attempts have creation and completion timestamps."""
        attempts = []
        
        for i in range(3):
            task = AcademicYearOrchestrator.create_import_task(
                academic_year=fresh_start_academic_year,
                task_type=ImportTask.TaskType.STUDENTS,
                total_records=100,
            )
            AcademicYearOrchestrator.report_import_started(task)
            
            if i == 2:
                # Last attempt succeeds
                AcademicYearOrchestrator.report_import_progress(
                    task, processed=100, success=100, errors=0
                )
                AcademicYearOrchestrator.report_import_completed(task)
            else:
                # Earlier attempts fail
                AcademicYearOrchestrator.report_import_failed(task)
            
            task.refresh_from_db()
            attempts.append(task)
        
        # Verify all have timestamps
        for task in attempts:
            assert task.created_at is not None
            assert task.completed_at is not None
    
    def test_can_view_complete_import_history(self, fresh_start_academic_year):
        """Verify can view complete import history for academic year."""
        # Create various import tasks
        grades_task1 = AcademicYearOrchestrator.create_import_task(
            academic_year=fresh_start_academic_year,
            task_type=ImportTask.TaskType.GRADES,
            total_records=50,
        )
        
        students_task1 = AcademicYearOrchestrator.create_import_task(
            academic_year=fresh_start_academic_year,
            task_type=ImportTask.TaskType.STUDENTS,
            total_records=200,
        )
        
        # Fail students task and retry
        AcademicYearOrchestrator.report_import_started(students_task1)
        AcademicYearOrchestrator.report_import_failed(students_task1)
        
        students_task2 = AcademicYearOrchestrator.create_import_task(
            academic_year=fresh_start_academic_year,
            task_type=ImportTask.TaskType.STUDENTS,
            total_records=200,
        )
        AcademicYearOrchestrator.report_import_started(students_task2)
        AcademicYearOrchestrator.report_import_completed(students_task2)
        
        # Query full history
        history = ImportTask.objects.filter(
            academic_year=fresh_start_academic_year
        ).order_by('created_at')
        
        assert history.count() == 3
        assert list(history.values_list('task_type', 'status')) == [
            (ImportTask.TaskType.GRADES, ImportTask.TaskStatus.PENDING),
            (ImportTask.TaskType.STUDENTS, ImportTask.TaskStatus.FAILED),
            (ImportTask.TaskType.STUDENTS, ImportTask.TaskStatus.COMPLETED),
        ]


@pytest.mark.django_db
class TestRetryWithDifferentData:
    """Test retrying with corrected or different data."""
    
    def test_retry_with_corrected_file_path(self, failed_import_task):
        """Verify retry can use corrected file path."""
        academic_year = failed_import_task.academic_year
        original_path = failed_import_task.file_path
        
        # Retry with corrected file
        retry_task = AcademicYearOrchestrator.create_import_task(
            academic_year=academic_year,
            task_type=failed_import_task.task_type,
            total_records=100,
            file_path="/uploads/students_fixed.csv",
        )
        
        assert retry_task.file_path != original_path
        assert retry_task.file_path == "/uploads/students_fixed.csv"
    
    def test_retry_with_different_record_count(self, failed_import_task):
        """Verify retry can have different record count."""
        academic_year = failed_import_task.academic_year
        
        # After fixing, file might have different number of records
        retry_task = AcademicYearOrchestrator.create_import_task(
            academic_year=academic_year,
            task_type=failed_import_task.task_type,
            total_records=95,  # 5 bad records removed
        )
        
        assert retry_task.total_records != failed_import_task.total_records
        assert retry_task.total_records == 95


@pytest.mark.django_db
class TestPartialImportRetry:
    """Test retrying partially failed imports."""
    
    def test_retry_partial_failure_with_only_failed_records(self, partial_failure_import_task):
        """Verify can retry with only the failed records."""
        academic_year = partial_failure_import_task.academic_year
        
        # Original: 500 total, 470 success, 30 failed
        assert partial_failure_import_task.error_count == 30
        
        # Retry with just the 30 failed records
        retry_task = AcademicYearOrchestrator.create_import_task(
            academic_year=academic_year,
            task_type=partial_failure_import_task.task_type,
            total_records=30,  # Only the failed records
            file_path="/uploads/students_failed_records_only.csv",
        )
        
        AcademicYearOrchestrator.report_import_started(retry_task)
        AcademicYearOrchestrator.report_import_progress(
            retry_task, processed=30, success=30, errors=0
        )
        AcademicYearOrchestrator.report_import_completed(retry_task)
        
        retry_task.refresh_from_db()
        
        # Verify retry succeeded
        assert retry_task.status == ImportTask.TaskStatus.COMPLETED
        assert retry_task.success_count == 30
        
        # Both tasks preserved
        all_tasks = ImportTask.objects.filter(
            academic_year=academic_year,
            task_type=partial_failure_import_task.task_type
        )
        assert all_tasks.count() == 2
    
    def test_combined_success_count_across_retries(self, fresh_start_academic_year):
        """Verify can calculate total success across original and retry."""
        # Original import: 100 total, 90 success, 10 failed
        original_task = AcademicYearOrchestrator.create_import_task(
            academic_year=fresh_start_academic_year,
            task_type=ImportTask.TaskType.STUDENTS,
            total_records=100,
        )
        AcademicYearOrchestrator.report_import_started(original_task)
        AcademicYearOrchestrator.report_import_progress(
            original_task, processed=100, success=90, errors=10
        )
        AcademicYearOrchestrator.report_import_completed(original_task)
        
        # Retry with 10 failed records: 8 success, 2 still fail
        retry_task = AcademicYearOrchestrator.create_import_task(
            academic_year=fresh_start_academic_year,
            task_type=ImportTask.TaskType.STUDENTS,
            total_records=10,
        )
        AcademicYearOrchestrator.report_import_started(retry_task)
        AcademicYearOrchestrator.report_import_progress(
            retry_task, processed=10, success=8, errors=2
        )
        AcademicYearOrchestrator.report_import_completed(retry_task)
        
        # Calculate total success
        all_tasks = ImportTask.objects.filter(
            academic_year=fresh_start_academic_year,
            task_type=ImportTask.TaskType.STUDENTS,
            status=ImportTask.TaskStatus.COMPLETED
        )
        
        total_success = sum(task.success_count for task in all_tasks)
        total_errors = sum(task.error_count for task in all_tasks)
        
        assert total_success == 98  # 90 + 8
        assert total_errors == 12   # 10 + 2


@pytest.mark.django_db
class TestRetryDoesNotAffectSetupProgress:
    """Test that failed/retry attempts don't incorrectly affect setup progress."""
    
    def test_failed_import_does_not_complete_setup_step(self, fresh_start_academic_year):
        """Verify failed import does not mark setup step as complete."""
        # Complete basic info
        AcademicYearOrchestrator.mark_step_complete(
            fresh_start_academic_year,
            AcademicYearSetup.SetupSteps.BASIC_INFO,
        )
        
        # Attempt grades import that fails
        task = AcademicYearOrchestrator.create_import_task(
            academic_year=fresh_start_academic_year,
            task_type=ImportTask.TaskType.GRADES,
            total_records=50,
        )
        AcademicYearOrchestrator.report_import_started(task)
        AcademicYearOrchestrator.report_import_failed(task)
        
        # Verify setup step not completed
        setup = fresh_start_academic_year.setup_progress
        setup.refresh_from_db()
        
        assert setup.import_grades_completed is False
        assert setup.current_step == AcademicYearSetup.SetupSteps.IMPORT_GRADES
    
    def test_successful_retry_completes_setup_step(self, fresh_start_academic_year):
        """Verify successful retry completes the setup step."""
        # Complete basic info
        AcademicYearOrchestrator.mark_step_complete(
            fresh_start_academic_year,
            AcademicYearSetup.SetupSteps.BASIC_INFO,
        )
        
        # First attempt fails
        task1 = AcademicYearOrchestrator.create_import_task(
            academic_year=fresh_start_academic_year,
            task_type=ImportTask.TaskType.GRADES,
            total_records=50,
        )
        AcademicYearOrchestrator.report_import_started(task1)
        AcademicYearOrchestrator.report_import_failed(task1)
        
        # Retry succeeds
        task2 = AcademicYearOrchestrator.create_import_task(
            academic_year=fresh_start_academic_year,
            task_type=ImportTask.TaskType.GRADES,
            total_records=50,
        )
        AcademicYearOrchestrator.report_import_started(task2)
        AcademicYearOrchestrator.report_import_progress(
            task2, processed=50, success=50, errors=0
        )
        AcademicYearOrchestrator.report_import_completed(task2)
        
        # Verify setup step completed
        setup = fresh_start_academic_year.setup_progress
        setup.refresh_from_db()
        
        assert setup.import_grades_completed is True
        assert setup.current_step == AcademicYearSetup.SetupSteps.IMPORT_STUDENTS
