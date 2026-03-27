"""
Pytest fixtures for academic_setup app tests.

This module provides comprehensive fixtures for testing academic year setup,
import tasks, and the orchestrator functionality.
"""

import pytest
from datetime import date, timedelta
from django.contrib.auth.models import Group

from applications.school_management.academic_management.models import AcademicYear
from applications.academic_setup.models import AcademicYearSetup, ImportTask
from applications.academic_setup.orchestrator import AcademicYearOrchestrator
from config.roles import RoleEnum


# ========================================================================
# DATE FIXTURES
# ========================================================================

@pytest.fixture
def current_date():
    """Provide current date for testing."""
    return date(2026, 9, 1)


@pytest.fixture
def academic_year_dates(current_date):
    """Provide standard academic year dates."""
    return {
        "start_date": current_date,
        "end_date": current_date + timedelta(days=365),
        "enrollment_start_date": current_date,
        "enrollment_end_date": current_date + timedelta(days=30),
    }


@pytest.fixture
def mid_year_dates(current_date):
    """Provide mid-year adoption dates."""
    return {
        "start_date": current_date,
        "end_date": current_date + timedelta(days=180),
    }


# ========================================================================
# ACADEMIC YEAR FIXTURES
# ========================================================================

@pytest.fixture
def fresh_start_academic_year(db, academic_year_dates):
    """Create a fresh start academic year in SETUP status."""
    return AcademicYearOrchestrator.create_academic_year(
        name="2026-2027",
        start_date=academic_year_dates["start_date"],
        end_date=academic_year_dates["end_date"],
        deployment_type=AcademicYear.DeploymentType.FRESH_START,
        enrollment_start_date=academic_year_dates["enrollment_start_date"],
        enrollment_end_date=academic_year_dates["enrollment_end_date"],
    )


@pytest.fixture
def mid_year_academic_year(db, mid_year_dates):
    """Create a mid-year academic year in SETUP status."""
    return AcademicYearOrchestrator.create_academic_year(
        name="2026-MidYear",
        start_date=mid_year_dates["start_date"],
        end_date=mid_year_dates["end_date"],
        deployment_type=AcademicYear.DeploymentType.MID_YEAR,
    )


@pytest.fixture
def active_academic_year(db, academic_year_dates):
    """Create an active academic year (setup completed)."""
    # Use dates from previous year
    prev_year_start = academic_year_dates["start_date"] - timedelta(days=365)
    prev_year_end = academic_year_dates["start_date"]
    
    academic_year = AcademicYearOrchestrator.create_academic_year(
        name="2025-2026-Active",
        start_date=prev_year_start,
        end_date=prev_year_end,
        deployment_type=AcademicYear.DeploymentType.FRESH_START,
        enrollment_start_date=prev_year_start,
        enrollment_end_date=prev_year_start + timedelta(days=30),
    )
    
    # Complete all setup steps
    setup = academic_year.setup_progress
    setup.basic_info_completed = True
    setup.import_grades_completed = True
    setup.import_students_completed = True
    setup.assign_classrooms_completed = True
    setup.review_completed = True
    setup.grades_import_method = AcademicYearSetup.ImportMethod.CSV
    setup.students_import_method = AcademicYearSetup.ImportMethod.CSV
    setup.classrooms_import_method = AcademicYearSetup.ImportMethod.MANUAL
    setup.current_step = AcademicYearSetup.SetupSteps.COMPLETED
    setup.save()
    
    # Transition to ACTIVE
    academic_year.status = AcademicYear.Status.ACTIVE
    academic_year.setup_completed = True
    academic_year.save()
    
    return academic_year


# ========================================================================
# ACADEMIC YEAR SETUP FIXTURES
# ========================================================================

@pytest.fixture
def basic_info_completed_setup(fresh_start_academic_year):
    """Academic year setup with basic info completed."""
    AcademicYearOrchestrator.mark_step_complete(
        fresh_start_academic_year,
        AcademicYearSetup.SetupSteps.BASIC_INFO,
    )
    fresh_start_academic_year.refresh_from_db()
    return fresh_start_academic_year.setup_progress


@pytest.fixture
def grades_imported_setup(fresh_start_academic_year):
    """Academic year setup with basic info and grades imported."""
    AcademicYearOrchestrator.mark_step_complete(
        fresh_start_academic_year,
        AcademicYearSetup.SetupSteps.BASIC_INFO,
    )
    AcademicYearOrchestrator.mark_step_complete(
        fresh_start_academic_year,
        AcademicYearSetup.SetupSteps.IMPORT_GRADES,
        import_method=AcademicYearSetup.ImportMethod.CSV,
    )
    fresh_start_academic_year.refresh_from_db()
    return fresh_start_academic_year.setup_progress


@pytest.fixture
def partially_completed_setup(fresh_start_academic_year):
    """Academic year setup with first 3 steps completed."""
    orchestrator = AcademicYearOrchestrator
    orchestrator.mark_step_complete(
        fresh_start_academic_year,
        AcademicYearSetup.SetupSteps.BASIC_INFO,
    )
    orchestrator.mark_step_complete(
        fresh_start_academic_year,
        AcademicYearSetup.SetupSteps.IMPORT_GRADES,
        import_method=AcademicYearSetup.ImportMethod.CSV,
    )
    orchestrator.mark_step_complete(
        fresh_start_academic_year,
        AcademicYearSetup.SetupSteps.IMPORT_STUDENTS,
        import_method=AcademicYearSetup.ImportMethod.CSV,
    )
    fresh_start_academic_year.refresh_from_db()
    return fresh_start_academic_year.setup_progress


@pytest.fixture
def fully_completed_setup(fresh_start_academic_year):
    """Academic year setup with all steps completed."""
    orchestrator = AcademicYearOrchestrator
    orchestrator.mark_step_complete(
        fresh_start_academic_year,
        AcademicYearSetup.SetupSteps.BASIC_INFO,
    )
    orchestrator.mark_step_complete(
        fresh_start_academic_year,
        AcademicYearSetup.SetupSteps.IMPORT_GRADES,
        import_method=AcademicYearSetup.ImportMethod.CSV,
    )
    orchestrator.mark_step_complete(
        fresh_start_academic_year,
        AcademicYearSetup.SetupSteps.IMPORT_STUDENTS,
        import_method=AcademicYearSetup.ImportMethod.CSV,
    )
    orchestrator.mark_step_complete(
        fresh_start_academic_year,
        AcademicYearSetup.SetupSteps.ASSIGN_CLASSROOMS,
        import_method=AcademicYearSetup.ImportMethod.MANUAL,
    )
    orchestrator.mark_step_complete(
        fresh_start_academic_year,
        AcademicYearSetup.SetupSteps.REVIEW,
    )
    fresh_start_academic_year.refresh_from_db()
    return fresh_start_academic_year.setup_progress


# ========================================================================
# IMPORT TASK FIXTURES
# ========================================================================

@pytest.fixture
def pending_grades_import_task(fresh_start_academic_year):
    """Create a pending grades import task."""
    return AcademicYearOrchestrator.create_import_task(
        academic_year=fresh_start_academic_year,
        task_type=ImportTask.TaskType.GRADES,
        total_records=100,
        file_path="/uploads/grades.csv",
    )


@pytest.fixture
def in_progress_import_task(fresh_start_academic_year):
    """Create an import task in progress."""
    task = AcademicYearOrchestrator.create_import_task(
        academic_year=fresh_start_academic_year,
        task_type=ImportTask.TaskType.STUDENTS,
        total_records=500,
        file_path="/uploads/students.csv",
    )
    AcademicYearOrchestrator.report_import_started(task)
    AcademicYearOrchestrator.report_import_progress(
        task,
        processed=250,
        success=240,
        errors=10,
    )
    task.refresh_from_db()
    return task


@pytest.fixture
def completed_import_task(fresh_start_academic_year):
    """Create a completed import task."""
    task = AcademicYearOrchestrator.create_import_task(
        academic_year=fresh_start_academic_year,
        task_type=ImportTask.TaskType.GRADES,
        total_records=50,
        file_path="/uploads/grades.csv",
    )
    AcademicYearOrchestrator.report_import_started(task)
    AcademicYearOrchestrator.report_import_progress(
        task,
        processed=50,
        success=50,
        errors=0,
    )
    AcademicYearOrchestrator.report_import_completed(task)
    task.refresh_from_db()
    return task


@pytest.fixture
def failed_import_task(fresh_start_academic_year):
    """Create a failed import task."""
    task = AcademicYearOrchestrator.create_import_task(
        academic_year=fresh_start_academic_year,
        task_type=ImportTask.TaskType.STUDENTS,
        total_records=100,
        file_path="/uploads/students_bad.csv",
    )
    AcademicYearOrchestrator.report_import_started(task)
    AcademicYearOrchestrator.report_import_failed(
        task,
        error_details={
            "error_type": "ValidationError",
            "message": "Invalid CSV format",
        }
    )
    task.refresh_from_db()
    return task


@pytest.fixture
def partial_failure_import_task(fresh_start_academic_year):
    """Create an import task with partial failures."""
    task = AcademicYearOrchestrator.create_import_task(
        academic_year=fresh_start_academic_year,
        task_type=ImportTask.TaskType.STUDENTS,
        total_records=500,
        file_path="/uploads/students_partial.csv",
    )
    AcademicYearOrchestrator.report_import_started(task)
    
    # Build error details with 30 errors
    error_list = [
        {"row": 15, "error": "Invalid email format"},
        {"row": 23, "error": "Missing required field"},
    ]
    # Add remaining errors to get to 30 total
    for i in range(3, 31):
        error_list.append({
            "row": 100 + i,
            "error": f"Validation error {i}",
        })
    
    AcademicYearOrchestrator.report_import_progress(
        task,
        processed=500,
        success=470,
        errors=30,
        error_details={"errors": error_list}
    )
    # Mark as completed even with errors
    AcademicYearOrchestrator.report_import_completed(task)
    task.refresh_from_db()
    return task


# ========================================================================
# GRADE FIXTURES
# ========================================================================

@pytest.fixture
def grade_data_list():
    """Provide sample grade data for bulk creation."""
    return [
        {"name": "Grade 1A", "grade": "1"},
        {"name": "Grade 1B", "grade": "1"},
        {"name": "Grade 2A", "grade": "2"},
        {"name": "Grade 2B", "grade": "2"},
        {"name": "Grade 3A", "grade": "3"},
        {"name": "Grade 3B", "grade": "3"},
        {"name": "Grade 4A", "grade": "4"},
        {"name": "Grade 5A", "grade": "5"},
        {"name": "Grade 6A", "grade": "6"},
    ]


@pytest.fixture
def created_grades(fresh_start_academic_year, grade_data_list):
    """Create sample grades for an academic year."""
    return AcademicYearOrchestrator.bulk_create_grades(
        fresh_start_academic_year,
        grade_data_list
    )


@pytest.fixture
def single_grade(fresh_start_academic_year):
    """Create a single grade for testing."""
    return AcademicYearOrchestrator.create_grade(
        academic_year=fresh_start_academic_year,
        name="Test Grade 1A",
        grade="1",
        description="Test grade for unit testing",
    )


# ========================================================================
# STUDENT FIXTURES (using user_management fixtures)
# ========================================================================

@pytest.fixture
def student_group(db):
    """Get or create STUDENT group."""
    group, _ = Group.objects.get_or_create(name=RoleEnum.STUDENT.value)
    return group


@pytest.fixture
def create_student_user(db, student_group):
    """Factory fixture for creating student users."""
    from applications.user_management.models import SchoolUser
    
    def _create_student(email=None, **kwargs):
        if email is None:
            import random
            email = f"student{random.randint(1000, 9999)}@school.com"
        
        user_data = {
            "email": email,
            "first_name": kwargs.get("first_name", "Test"),
            "last_name": kwargs.get("last_name", "Student"),
        }
        return SchoolUser.objects.create_student(**user_data)
    
    return _create_student


@pytest.fixture
def sample_students(create_student_user):
    """Create multiple student users for testing."""
    return [
        create_student_user(email=f"student{i}@test.com", first_name=f"Student{i}")
        for i in range(1, 11)
    ]


# ========================================================================
# CSV DATA FIXTURES
# ========================================================================

@pytest.fixture
def csv_grades_data():
    """Provide sample CSV grades data."""
    return [
        {"name": "KG-A", "grade": "KG", "grade_type": "Kindergarten"},
        {"name": "KG-B", "grade": "KG", "grade_type": "Kindergarten"},
        {"name": "1-A", "grade": "1", "grade_type": "Elementary"},
        {"name": "1-B", "grade": "1", "grade_type": "Elementary"},
        {"name": "2-A", "grade": "2", "grade_type": "Elementary"},
    ]


@pytest.fixture
def csv_students_data():
    """Provide sample CSV student data."""
    return [
        {
            "email": f"student{i}@csv.com",
            "first_name": f"CSVStudent{i}",
            "last_name": "Test",
            "grade": "1",
        }
        for i in range(1, 101)
    ]


@pytest.fixture
def csv_with_errors_data():
    """Provide CSV data with some invalid records."""
    valid_records = [
        {
            "email": f"valid{i}@csv.com",
            "first_name": f"Valid{i}",
            "last_name": "Student",
        }
        for i in range(1, 471)
    ]
    
    invalid_records = [
        {"email": "invalid-email", "first_name": "Bad1", "last_name": "Student"},
        {"email": "", "first_name": "Bad2", "last_name": "Student"},
        {"first_name": "Bad3", "last_name": "Student"},  # Missing email
        # ... more invalid records
    ] * 10  # 30 invalid records
    
    return valid_records + invalid_records[:30]


# ========================================================================
# UTILITY FIXTURES
# ========================================================================

@pytest.fixture
def orchestrator():
    """Provide the orchestrator class for convenience."""
    return AcademicYearOrchestrator
