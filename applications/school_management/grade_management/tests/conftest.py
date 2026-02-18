"""
Fixtures for grade_management tests.

This module provides test fixtures for:
- Academic years in different statuses (SETUP, ENROLLMENT, ACTIVE, COMPLETED)
- Grades for different academic year phases
- Student users for enrollment testing
- Sample enrollment data
"""

import pytest
from datetime import date, timedelta
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from applications.school_management.academic_management.models import AcademicYear, StudentEnrollment
from applications.school_management.grade_management.models import Grade
from applications.academic_setup.models import AcademicYearSetup
from config.roles import RoleEnum

User = get_user_model()


# ========================================================================
# DATE FIXTURES
# ========================================================================

@pytest.fixture
def base_date():
    """Base date for consistent test data."""
    return date(2026, 1, 1)


@pytest.fixture
def academic_year_dates(base_date):
    """Standard academic year date range."""
    return {
        "start_date": base_date,
        "end_date": base_date + timedelta(days=365),
        "enrollment_start": base_date + timedelta(days=30),
        "enrollment_end": base_date + timedelta(days=90),
    }


# ========================================================================
# ACADEMIC YEAR FIXTURES - BY STATUS
# ========================================================================

@pytest.fixture
def setup_academic_year(db, academic_year_dates):
    """Create an academic year in SETUP status."""
    ay = AcademicYear.objects.create(
        name="2026/2027",
        start_date=academic_year_dates["start_date"],
        end_date=academic_year_dates["end_date"],
        enrollment_start_date=academic_year_dates["enrollment_start"],
        enrollment_end_date=academic_year_dates["enrollment_end"],
        status=AcademicYear.Status.SETUP,
        deployment_type=AcademicYear.DeploymentType.FRESH_START,
        setup_completed=False,
        is_active=True,
    )
    # Create setup progress tracker
    AcademicYearSetup.objects.create(
        academic_year=ay,
        current_step=AcademicYearSetup.SetupSteps.BASIC_INFO,
        basic_info_completed=False,
    )
    return ay


@pytest.fixture
def enrollment_academic_year(db, academic_year_dates):
    """Create an academic year in ENROLLMENT status."""
    ay = AcademicYear.objects.create(
        name="2026/2027 Enrollment",
        start_date=academic_year_dates["start_date"],
        end_date=academic_year_dates["end_date"],
        enrollment_start_date=academic_year_dates["enrollment_start"],
        enrollment_end_date=academic_year_dates["enrollment_end"],
        status=AcademicYear.Status.ENROLLMENT,
        deployment_type=AcademicYear.DeploymentType.FRESH_START,
        setup_completed=True,
        is_active=True,
    )
    # Create setup progress tracker (all completed)
    AcademicYearSetup.objects.create(
        academic_year=ay,
        current_step=AcademicYearSetup.SetupSteps.REVIEW,
        basic_info_completed=True,
        import_grades_completed=True,
        import_students_completed=True,
        assign_classrooms_completed=True,
        review_completed=True,
    )
    return ay


@pytest.fixture
def active_academic_year(db, academic_year_dates):
    """Create an academic year in ACTIVE status."""
    ay = AcademicYear.objects.create(
        name="2026/2027 Active",
        start_date=academic_year_dates["start_date"],
        end_date=academic_year_dates["end_date"],
        enrollment_start_date=academic_year_dates["enrollment_start"],
        enrollment_end_date=academic_year_dates["enrollment_end"],
        status=AcademicYear.Status.ACTIVE,
        deployment_type=AcademicYear.DeploymentType.FRESH_START,
        setup_completed=True,
        is_active=True,
    )
    return ay


@pytest.fixture
def completed_academic_year(db, base_date):
    """Create an academic year in COMPLETED status."""
    past_start = base_date - timedelta(days=730)  # 2 years ago
    past_end = base_date - timedelta(days=365)    # 1 year ago
    
    ay = AcademicYear.objects.create(
        name="2024/2025 Completed",
        start_date=past_start,
        end_date=past_end,
        enrollment_start_date=past_start + timedelta(days=30),
        enrollment_end_date=past_start + timedelta(days=90),
        status=AcademicYear.Status.COMPLETED,
        deployment_type=AcademicYear.DeploymentType.FRESH_START,
        setup_completed=True,
        is_active=False,
    )
    return ay


# ========================================================================
# ACADEMIC YEAR FIXTURES - FOR YEARLY COMPARISON
# ========================================================================

@pytest.fixture
def previous_academic_year(db, base_date):
    """Create previous year's academic year for testing cross-year scenarios."""
    past_start = base_date - timedelta(days=730)
    past_end = base_date - timedelta(days=365)
    
    ay = AcademicYear.objects.create(
        name="2025/2026",
        start_date=past_start,
        end_date=past_end,
        status=AcademicYear.Status.SETUP,  # Allow grade creation for testing
        deployment_type=AcademicYear.DeploymentType.FRESH_START,
        setup_completed=False,
        is_active=False,
    )
    return ay


# ========================================================================
# GRADE FIXTURES - BY ACADEMIC YEAR STATUS
# ========================================================================

@pytest.fixture
def grade_in_setup(setup_academic_year):
    """Create a grade during SETUP phase."""
    return Grade.objects.create(
        name="Class A",
        grade="Grade 10",
        grade_type="Secondary",
        academic_year=setup_academic_year,
        description="Grade 10 Section A - Setup Phase",
        is_active=True,
    )


@pytest.fixture
def grade_in_enrollment(enrollment_academic_year):
    """Create a grade during ENROLLMENT phase."""
    return Grade.objects.create(
        name="Class B",
        grade="Grade 10",
        grade_type="Secondary",
        academic_year=enrollment_academic_year,
        description="Grade 10 Section B - Enrollment Phase",
        is_active=True,
    )


@pytest.fixture
def grade_in_active(db, academic_year_dates):
    """Create a grade during ACTIVE phase (created before activation)."""
    # Create academic year in SETUP status first
    ay = AcademicYear.objects.create(
        name="2026/2027 Active",
        start_date=academic_year_dates["start_date"],
        end_date=academic_year_dates["end_date"],
        enrollment_start_date=academic_year_dates["enrollment_start"],
        enrollment_end_date=academic_year_dates["enrollment_end"],
        status=AcademicYear.Status.SETUP,
        deployment_type=AcademicYear.DeploymentType.FRESH_START,
        setup_completed=False,
        is_active=True,
    )
    
    # Create grade while in valid status
    grade = Grade.objects.create(
        name="Class C",
        grade="Grade 10",
        grade_type="Secondary",
        academic_year=ay,
        description="Grade 10 Section C - Active Phase",
        is_active=True,
    )
    
    # Now transition to ACTIVE status
    ay.status = AcademicYear.Status.ACTIVE
    ay.setup_completed = True
    ay.save()
    
    return grade


@pytest.fixture
def grade_in_completed(db, base_date):
    """Create a grade in a COMPLETED academic year."""
    past_start = base_date - timedelta(days=730)  # 2 years ago
    past_end = base_date - timedelta(days=365)    # 1 year ago
    
    # Create academic year in SETUP status first
    ay = AcademicYear.objects.create(
        name="2024/2025 Completed",
        start_date=past_start,
        end_date=past_end,
        enrollment_start_date=past_start + timedelta(days=30),
        enrollment_end_date=past_start + timedelta(days=90),
        status=AcademicYear.Status.SETUP,
        deployment_type=AcademicYear.DeploymentType.FRESH_START,
        setup_completed=False,
        is_active=False,
    )
    
    # Create grade while in valid status
    grade = Grade.objects.create(
        name="Class D",
        grade="Grade 10",
        grade_type="Secondary",
        academic_year=ay,
        description="Grade 10 Section D - Completed",
        is_active=True,
    )
    
    # Now transition to COMPLETED status
    ay.status = AcademicYear.Status.COMPLETED
    ay.setup_completed = True
    ay.save()
    
    return grade


# ========================================================================
# MULTIPLE GRADES FIXTURES
# ========================================================================

@pytest.fixture
def multiple_grades_same_year(enrollment_academic_year):
    """Create multiple grades in the same academic year with different sections."""
    grades = []
    for section in ["A", "B", "C"]:
        grade = Grade.objects.create(
            name=f"Class {section}",
            grade="Grade 10",
            grade_type="Secondary",
            academic_year=enrollment_academic_year,
            description=f"Grade 10 Section {section}",
            is_active=True,
        )
        grades.append(grade)
    return grades


@pytest.fixture
def same_name_different_years(setup_academic_year, previous_academic_year):
    """Create grades with same name in different academic years."""
    grade_current = Grade.objects.create(
        name="Class A",
        grade="Grade 10",
        grade_type="Secondary",
        academic_year=setup_academic_year,
        description="Grade 10 Class A - Current Year",
        is_active=True,
    )
    
    grade_previous = Grade.objects.create(
        name="Class A",
        grade="Grade 10",
        grade_type="Secondary",
        academic_year=previous_academic_year,
        description="Grade 10 Class A - Previous Year",
        is_active=True,
    )
    
    return {"current": grade_current, "previous": grade_previous}


# ========================================================================
# USER/STUDENT FIXTURES
# ========================================================================

@pytest.fixture
def student_role(db):
    """Create or get STUDENT role group."""
    group, _ = Group.objects.get_or_create(name=RoleEnum.STUDENT.value)
    return group


@pytest.fixture
def student_user(db, student_role):
    """Create a single student user for enrollment testing."""
    user = User.objects.create_user(
        email="student001@school.edu",
        password="testpass123",
        first_name="John",
        last_name="Doe",
    )
    user.groups.add(student_role)
    return user


@pytest.fixture
def student_user_2(db, student_role):
    """Create a second student user."""
    user = User.objects.create_user(
        email="student002@school.edu",
        password="testpass123",
        first_name="Jane",
        last_name="Smith",
    )
    user.groups.add(student_role)
    return user


@pytest.fixture
def student_user_3(db, student_role):
    """Create a third student user."""
    user = User.objects.create_user(
        email="student003@school.edu",
        password="testpass123",
        first_name="Bob",
        last_name="Johnson",
    )
    user.groups.add(student_role)
    return user


@pytest.fixture
def multiple_student_users(db, student_role):
    """Create multiple student users."""
    users = []
    for i in range(1, 6):
        user = User.objects.create_user(
            email=f"student{i:03d}@school.edu",
            password="testpass123",
            first_name=f"Student{i}",
            last_name=f"Test{i}",
        )
        user.groups.add(student_role)
        users.append(user)
    return users


@pytest.fixture
def non_student_user(db):
    """Create a user WITHOUT student role."""
    user = User.objects.create_user(
        email="teacher001@school.edu",
        password="testpass123",
        first_name="Teacher",
        last_name="Person",
    )
    return user


# ========================================================================
# ENROLLMENT FIXTURES
# ========================================================================

@pytest.fixture
def enrolled_student(grade_in_enrollment, student_user):
    """Create a student enrollment."""
    enrollment = StudentEnrollment.objects.create(
        student=student_user,
        grade=grade_in_enrollment,
        academic_year=grade_in_enrollment.academic_year,
    )
    return enrollment


@pytest.fixture
def multiple_enrollments(multiple_grades_same_year, multiple_student_users):
    """Create multiple student enrollments across different grades."""
    enrollments = []
    for grade, student in zip(multiple_grades_same_year, multiple_student_users, strict=False):
        enrollment = StudentEnrollment.objects.create(
            student=student,
            grade=grade,
            academic_year=grade.academic_year,
        )
        enrollments.append(enrollment)
    return enrollments


# ========================================================================
# VALIDATION TEST DATA
# ========================================================================

@pytest.fixture
def valid_grade_data():
    """Provide valid grade creation data."""
    return {
        "name": "Class A",
        "grade": "Grade 10",
        "grade_type": "Secondary",
        "grade_subtype": "",
        "description": "Test grade",
    }


@pytest.fixture
def invalid_grade_levels():
    """Provide invalid grade level values for validation testing."""
    return {
        "empty": "",
        "blank_spaces": "      ",
        "too_long": "VeryVeryVeryVeryLongGradeDefinitionThatExceedsTheMaximumLength",
        "none": None,
    }
