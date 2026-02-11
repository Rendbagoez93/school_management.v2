"""
Pytest fixtures for academic_setup tests.

Provides fixtures for AcademicYear, AcademicYearSetup, and ImportTask testing.
"""

from datetime import date, timedelta

import pytest

from applications.school_management.academic_management.models import AcademicYear
from applications.academic_setup.models import AcademicYearSetup, ImportTask


@pytest.fixture
def academic_year():
    """Create a basic academic year for testing."""
    return AcademicYear.objects.create(
        name="2025-2026",
        start_date=date(2025, 9, 1),
        end_date=date(2026, 6, 30),
        is_active=True,
        status=AcademicYear.Status.SETUP,
        deployment_type=AcademicYear.DeploymentType.FRESH_START,
    )


@pytest.fixture
def academic_year_with_enrollment():
    """Create an academic year with enrollment period configured."""
    return AcademicYear.objects.create(
        name="2026-2027",
        start_date=date(2026, 9, 1),
        end_date=date(2027, 6, 30),
        is_active=True,
        status=AcademicYear.Status.SETUP,
        deployment_type=AcademicYear.DeploymentType.FRESH_START,
        enrollment_start_date=date(2026, 7, 1),
        enrollment_end_date=date(2026, 8, 31),
    )


@pytest.fixture
def completed_academic_year():
    """Create a completed academic year for testing."""
    return AcademicYear.objects.create(
        name="2024-2025",
        start_date=date(2024, 9, 1),
        end_date=date(2025, 6, 30),
        is_active=False,
        status=AcademicYear.Status.COMPLETED,
        deployment_type=AcademicYear.DeploymentType.FRESH_START,
        setup_completed=True,
    )


@pytest.fixture
def academic_year_setup(academic_year):
    """Create a basic academic year setup instance."""
    return AcademicYearSetup.objects.create(
        academic_year=academic_year,
    )


@pytest.fixture
def partial_setup(academic_year):
    """Create a partially completed setup."""
    return AcademicYearSetup.objects.create(
        academic_year=academic_year,
        basic_info_completed=True,
        import_grades_completed=True,
        grades_import_method=AcademicYearSetup.ImportMethod.CSV,
        current_step=AcademicYearSetup.SetupSteps.IMPORT_STUDENTS,
    )


@pytest.fixture
def fully_completed_setup(academic_year):
    """Create a fully completed setup."""
    return AcademicYearSetup.objects.create(
        academic_year=academic_year,
        basic_info_completed=True,
        import_grades_completed=True,
        import_students_completed=True,
        assign_classrooms_completed=True,
        review_completed=True,
        grades_import_method=AcademicYearSetup.ImportMethod.CSV,
        students_import_method=AcademicYearSetup.ImportMethod.CSV,
        classrooms_import_method=AcademicYearSetup.ImportMethod.MANUAL,
        current_step=AcademicYearSetup.SetupSteps.COMPLETED,
    )


@pytest.fixture
def import_task_pending(academic_year):
    """Create a pending import task."""
    return ImportTask.objects.create(
        academic_year=academic_year,
        task_type=ImportTask.TaskType.STUDENTS,
        status=ImportTask.TaskStatus.PENDING,
        total_records=0,
        processed_records=0,
    )


@pytest.fixture
def import_task_in_progress(academic_year):
    """Create an in-progress import task."""
    return ImportTask.objects.create(
        academic_year=academic_year,
        task_type=ImportTask.TaskType.GRADES,
        status=ImportTask.TaskStatus.IN_PROGRESS,
        file_path="/uploads/grades_2025.csv",
        total_records=100,
        processed_records=25,
        success_count=24,
        error_count=1,
    )


@pytest.fixture
def import_task_completed(academic_year):
    """Create a completed import task."""
    return ImportTask.objects.create(
        academic_year=academic_year,
        task_type=ImportTask.TaskType.CLASSROOMS,
        status=ImportTask.TaskStatus.COMPLETED,
        file_path="/uploads/classrooms.csv",
        total_records=50,
        processed_records=50,
        success_count=50,
        error_count=0,
    )


@pytest.fixture
def import_task_with_errors(academic_year):
    """Create a failed import task with error details."""
    return ImportTask.objects.create(
        academic_year=academic_year,
        task_type=ImportTask.TaskType.STUDENTS,
        status=ImportTask.TaskStatus.FAILED,
        file_path="/uploads/students_bad.csv",
        total_records=10,
        processed_records=10,
        success_count=7,
        error_count=3,
        error_details={
            "errors": [
                {"row": 3, "error": "Invalid email format"},
                {"row": 5, "error": "Missing required field: last_name"},
                {"row": 8, "error": "Duplicate student ID"},
            ]
        },
    )
