"""
Pytest fixtures for academic_management app tests.

Provides comprehensive fixtures for testing academic year lifecycle,
enrollment periods, and status transitions.
"""

import pytest
from datetime import date, timedelta
from django.contrib.auth import get_user_model

from applications.school_management.academic_management.models import (
    AcademicYear,
    StudentEnrollment,
)
from applications.school_management.grade_management.models import Grade


User = get_user_model()


# ========================================================================
# DATE FIXTURES
# ========================================================================

@pytest.fixture
def base_date():
    """Provide consistent base date for testing."""
    return date(2026, 7, 1)


@pytest.fixture
def academic_year_dates(base_date):
    """Provide standard academic year dates (2026/2027)."""
    return {
        "start_date": base_date,  # 2026-07-01
        "end_date": base_date + timedelta(days=364),  # 2027-06-30
        "enrollment_start_date": base_date - timedelta(days=16),  # 2026-06-15
        "enrollment_end_date": base_date + timedelta(days=14),  # 2026-07-15
    }


@pytest.fixture
def invalid_date_range(base_date):
    """Provide invalid date range where start >= end."""
    return {
        "start_date": base_date,
        "end_date": base_date - timedelta(days=1),  # Before start!
    }


@pytest.fixture
def mid_year_dates(base_date):
    """Provide mid-year adoption dates (starts mid-semester)."""
    # School joins in January, mid-way through academic year
    mid_year_start = date(2027, 1, 15)
    return {
        "start_date": mid_year_start,
        "end_date": mid_year_start + timedelta(days=165),  # About 5.5 months
    }


# ========================================================================
# ACADEMIC YEAR FIXTURES - FRESH START
# ========================================================================

@pytest.fixture
def fresh_start_academic_year(db, academic_year_dates):
    """
    Create a fresh start academic year in SETUP status.
    
    Use case 1: Creating a New Academic Year (Fresh Start)
    - Name: 2026 / 2027
    - Start: 2026-07-01
    - End: 2027-06-30
    - Deployment: FRESH_START
    - Status: SETUP (default)
    - setup_completed: False (default)
    """
    return AcademicYear.objects.create(
        name="2026 / 2027",
        start_date=academic_year_dates["start_date"],
        end_date=academic_year_dates["end_date"],
        deployment_type=AcademicYear.DeploymentType.FRESH_START,
        status=AcademicYear.Status.SETUP,
        setup_completed=False,
    )


@pytest.fixture
def academic_year_with_enrollment_period(db, academic_year_dates):
    """
    Create academic year with defined enrollment period.
    
    Use case 2: Defining Enrollment Period
    - Enrollment Start: 2026-06-15
    - Enrollment End: 2026-07-15
    """
    return AcademicYear.objects.create(
        name="2026 / 2027 - With Enrollment",
        start_date=academic_year_dates["start_date"],
        end_date=academic_year_dates["end_date"],
        deployment_type=AcademicYear.DeploymentType.FRESH_START,
        enrollment_start_date=academic_year_dates["enrollment_start_date"],
        enrollment_end_date=academic_year_dates["enrollment_end_date"],
        status=AcademicYear.Status.SETUP,
    )


@pytest.fixture
def setup_completed_academic_year(db, academic_year_dates):
    """
    Create academic year with setup completed.
    
    Use case 3: Setup Completion Flow
    - Grades defined
    - Subjects assigned
    - Curriculum mapped
    - setup_completed = True
    - Status moves to ENROLLMENT or ACTIVE
    """
    return AcademicYear.objects.create(
        name="2026 / 2027 - Setup Complete",
        start_date=academic_year_dates["start_date"],
        end_date=academic_year_dates["end_date"],
        deployment_type=AcademicYear.DeploymentType.FRESH_START,
        enrollment_start_date=academic_year_dates["enrollment_start_date"],
        enrollment_end_date=academic_year_dates["enrollment_end_date"],
        status=AcademicYear.Status.ENROLLMENT,
        setup_completed=True,
    )


# ========================================================================
# ACADEMIC YEAR FIXTURES - MID-YEAR ADOPTION
# ========================================================================

@pytest.fixture
def mid_year_academic_year(db, mid_year_dates):
    """
    Create mid-year adoption academic year.
    
    Use case 4: Mid-Year Adoption
    - School joins platform mid-semester
    - Deployment: MID_YEAR
    - Status: ACTIVE (not ENROLLMENT)
    - Enrollment period: null (not applicable)
    """
    return AcademicYear.objects.create(
        name="2027 Mid-Year",
        start_date=mid_year_dates["start_date"],
        end_date=mid_year_dates["end_date"],
        deployment_type=AcademicYear.DeploymentType.MID_YEAR,
        status=AcademicYear.Status.ACTIVE,
        setup_completed=True,
        # No enrollment period for mid-year
        enrollment_start_date=None,
        enrollment_end_date=None,
    )


# ========================================================================
# ACADEMIC YEAR FIXTURES - ACTIVE & COMPLETED
# ========================================================================

@pytest.fixture
def active_academic_year(db, academic_year_dates):
    """
    Create an active academic year.
    
    Use case 5: Academic Year Activation
    - Status: ACTIVE
    - setup_completed: True
    - Teaching/Attendance allowed
    - Grade creation typically locked
    - Student enrollment typically frozen
    """
    return AcademicYear.objects.create(
        name="2025 / 2026 - Active",
        start_date=academic_year_dates["start_date"] - timedelta(days=365),
        end_date=academic_year_dates["start_date"] - timedelta(days=1),
        deployment_type=AcademicYear.DeploymentType.FRESH_START,
        status=AcademicYear.Status.ACTIVE,
        setup_completed=True,
    )


@pytest.fixture
def completed_academic_year(db, base_date):
    """
    Create a completed academic year.
    
    Use case 6: Academic Year Completion
    - Status: COMPLETED
    - No structural edits allowed
    - No enrollments allowed
    - Reports/archives allowed
    - Triggers promotion/rollover logic
    """
    # Previous year that has ended
    return AcademicYear.objects.create(
        name="2024 / 2025 - Completed",
        start_date=base_date - timedelta(days=730),  # 2 years ago
        end_date=base_date - timedelta(days=366),  # 1 year + 1 day ago
        deployment_type=AcademicYear.DeploymentType.FRESH_START,
        status=AcademicYear.Status.COMPLETED,
        setup_completed=True,
    )


# ========================================================================
# GRADE FIXTURES
# ========================================================================

@pytest.fixture
def grade_for_setup_year(fresh_start_academic_year):
    """Create a grade for academic year in SETUP status."""
    return Grade.objects.create(
        name="Class 1A",
        grade="1",
        grade_type="Primary",
        academic_year=fresh_start_academic_year,
        description="First grade section A",
    )


@pytest.fixture
def grade_for_enrollment_year(setup_completed_academic_year):
    """Create a grade for academic year in ENROLLMENT status."""
    return Grade.objects.create(
        name="Class 2B",
        grade="2",
        grade_type="Primary",
        academic_year=setup_completed_academic_year,
        description="Second grade section B",
    )


@pytest.fixture
def grade_for_active_year(active_academic_year):
    """Create a grade for active academic year."""
    return Grade.objects.create(
        name="Class 3C",
        grade="3",
        grade_type="Primary",
        academic_year=active_academic_year,
        description="Third grade section C",
    )


# ========================================================================
# USER/STUDENT FIXTURES
# ========================================================================

@pytest.fixture
def student_user(db):
    """Create a student user for enrollment testing."""
    return User.objects.create_user(
        username="student001",
        email="student001@school.edu",
        first_name="John",
        last_name="Doe",
    )


@pytest.fixture
def student_users(db):
    """Create multiple student users for enrollment testing."""
    students = []
    for i in range(1, 6):
        student = User.objects.create_user(
            username=f"student{i:03d}",
            email=f"student{i:03d}@school.edu",
            first_name=f"Student{i}",
            last_name="User",
        )
        students.append(student)
    return students


# ========================================================================
# ENROLLMENT FIXTURES
# ========================================================================

@pytest.fixture
def student_enrollment(student_user, grade_for_enrollment_year, setup_completed_academic_year):
    """Create a student enrollment for testing."""
    return StudentEnrollment.objects.create(
        student=student_user,
        grade=grade_for_enrollment_year,
        academic_year=setup_completed_academic_year,
    )


@pytest.fixture
def multiple_enrollments(student_users, grade_for_enrollment_year, setup_completed_academic_year):
    """Create multiple student enrollments."""
    enrollments = []
    for student in student_users[:3]:  # Enroll first 3 students
        enrollment = StudentEnrollment.objects.create(
            student=student,
            grade=grade_for_enrollment_year,
            academic_year=setup_completed_academic_year,
        )
        enrollments.append(enrollment)
    return enrollments


# ========================================================================
# VALIDATION TESTING FIXTURES
# ========================================================================

@pytest.fixture
def invalid_enrollment_dates(academic_year_dates):
    """Provide invalid enrollment dates (outside academic year range)."""
    return {
        "enrollment_start_date": academic_year_dates["start_date"] - timedelta(days=60),
        "enrollment_end_date": academic_year_dates["end_date"] + timedelta(days=30),
    }


@pytest.fixture
def partial_enrollment_dates(academic_year_dates):
    """Provide only one enrollment date (should fail validation)."""
    return {
        "enrollment_start_date": academic_year_dates["enrollment_start_date"],
        "enrollment_end_date": None,  # Missing end date
    }
