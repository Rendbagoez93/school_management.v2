"""
Test Use Case 2: Defining Enrollment Period

Real-World Scenario:
Admin sets enrollment period for academic year:
- Enrollment Start → 2026-06-15
- Enrollment End → 2026-07-15

Expectations:
✔ Valid if: start_date <= enrollment_start < enrollment_end <= end_date
✔ System behavior:
  - Academic year may move → ENROLLMENT status
  - StudentEnrollment records → Allowed
✘ Invalid cases:
  - Only one enrollment date set (must be both or neither)
  - Enrollment period outside academic year boundaries
  - Enrollment start >= enrollment end
"""

import pytest
from datetime import timedelta
from django.core.exceptions import ValidationError

from applications.school_management.academic_management.models import (
    AcademicYear,
    StudentEnrollment,
)
from applications.school_management.grade_management.models import Grade


@pytest.mark.django_db
class TestEnrollmentPeriodDefinition:
    """Test defining enrollment period for academic year."""
    
    def test_valid_enrollment_period_within_academic_year(self, academic_year_dates):
        """Test setting a valid enrollment period within academic year dates."""
        academic_year = AcademicYear.objects.create(
            name="2026 / 2027",
            start_date=academic_year_dates["start_date"],
            end_date=academic_year_dates["end_date"],
            deployment_type=AcademicYear.DeploymentType.FRESH_START,
            enrollment_start_date=academic_year_dates["enrollment_start_date"],
            enrollment_end_date=academic_year_dates["enrollment_end_date"],
        )
        
        # Verify enrollment period was set
        assert academic_year.enrollment_start_date == academic_year_dates["enrollment_start_date"]
        assert academic_year.enrollment_end_date == academic_year_dates["enrollment_end_date"]
        
        # Verify dates are in correct order
        assert academic_year.start_date <= academic_year.enrollment_start_date
        assert academic_year.enrollment_start_date < academic_year.enrollment_end_date
        assert academic_year.enrollment_end_date <= academic_year.end_date
        
        # Should pass validation
        academic_year.full_clean()
    
    def test_enrollment_period_at_start_of_academic_year(self, base_date):
        """Test enrollment period that starts with academic year."""
        academic_year = AcademicYear.objects.create(
            name="Enrollment at Start",
            start_date=base_date,
            end_date=base_date + timedelta(days=365),
            enrollment_start_date=base_date,  # Same as start_date
            enrollment_end_date=base_date + timedelta(days=30),
        )
        
        academic_year.full_clean()  # Should not raise
        assert academic_year.enrollment_start_date == academic_year.start_date
    
    def test_enrollment_period_at_end_of_academic_year(self, base_date):
        """Test enrollment period that ends with academic year."""
        academic_year = AcademicYear.objects.create(
            name="Enrollment at End",
            start_date=base_date,
            end_date=base_date + timedelta(days=365),
            enrollment_start_date=base_date + timedelta(days=335),
            enrollment_end_date=base_date + timedelta(days=365),  # Same as end_date
        )
        
        academic_year.full_clean()  # Should not raise
        assert academic_year.enrollment_end_date == academic_year.end_date
    
    def test_enrollment_before_academic_year_start(self, base_date):
        """Test that enrollment starting before academic year raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            academic_year = AcademicYear.objects.create(
                name="Early Enrollment",
                start_date=base_date,
                end_date=base_date + timedelta(days=365),
                enrollment_start_date=base_date - timedelta(days=30),  # Before start
                enrollment_end_date=base_date + timedelta(days=15),
            )
        
        # Model currently requires enrollment period within academic year dates
        assert "Enrollment period must be within academic year dates" in str(exc_info.value)


@pytest.mark.django_db
class TestEnrollmentPeriodValidation:
    """Test validation rules for enrollment period."""
    
    def test_both_enrollment_dates_required(self, academic_year_dates):
        """Test that both enrollment dates must be set or both null."""
        # Only start date set
        academic_year = AcademicYear(
            name="Partial Enrollment 1",
            start_date=academic_year_dates["start_date"],
            end_date=academic_year_dates["end_date"],
            enrollment_start_date=academic_year_dates["enrollment_start_date"],
            enrollment_end_date=None,  # Missing end date
        )
        
        with pytest.raises(ValidationError) as exc_info:
            academic_year.full_clean()
        
        assert "Both enrollment start and end dates must be set" in str(exc_info.value)
    
    def test_only_end_date_set_is_invalid(self, academic_year_dates):
        """Test that only setting enrollment end date is invalid."""
        academic_year = AcademicYear(
            name="Partial Enrollment 2",
            start_date=academic_year_dates["start_date"],
            end_date=academic_year_dates["end_date"],
            enrollment_start_date=None,  # Missing start date
            enrollment_end_date=academic_year_dates["enrollment_end_date"],
        )
        
        with pytest.raises(ValidationError) as exc_info:
            academic_year.full_clean()
        
        assert "Both enrollment start and end dates must be set" in str(exc_info.value)
    
    def test_both_enrollment_dates_null_is_valid(self, academic_year_dates):
        """Test that both enrollment dates can be null (valid for mid-year)."""
        academic_year = AcademicYear.objects.create(
            name="No Enrollment Period",
            start_date=academic_year_dates["start_date"],
            end_date=academic_year_dates["end_date"],
            enrollment_start_date=None,
            enrollment_end_date=None,
        )
        
        academic_year.full_clean()  # Should not raise
        assert academic_year.enrollment_start_date is None
        assert academic_year.enrollment_end_date is None
    
    def test_enrollment_end_after_academic_year_is_invalid(self, base_date):
        """Test that enrollment end date cannot be after academic year end."""
        academic_year = AcademicYear(
            name="Enrollment Overflow",
            start_date=base_date,
            end_date=base_date + timedelta(days=365),
            enrollment_start_date=base_date,
            enrollment_end_date=base_date + timedelta(days=400),  # After academic year
        )
        
        with pytest.raises(ValidationError) as exc_info:
            academic_year.full_clean()
        
        assert "Enrollment period must be within academic year dates" in str(exc_info.value)
    
    def test_enrollment_start_equal_to_end_is_invalid(self, base_date):
        """Test that enrollment start must be before end."""
        academic_year = AcademicYear(
            name="Same Enrollment Dates",
            start_date=base_date,
            end_date=base_date + timedelta(days=365),
            enrollment_start_date=base_date + timedelta(days=10),
            enrollment_end_date=base_date + timedelta(days=10),  # Same as start
        )
        
        with pytest.raises(ValidationError) as exc_info:
            academic_year.full_clean()
        
        assert "Enrollment period must be within academic year dates" in str(exc_info.value)
    
    def test_enrollment_start_after_end_is_invalid(self, base_date):
        """Test that enrollment start cannot be after end."""
        academic_year = AcademicYear(
            name="Reversed Enrollment",
            start_date=base_date,
            end_date=base_date + timedelta(days=365),
            enrollment_start_date=base_date + timedelta(days=60),
            enrollment_end_date=base_date + timedelta(days=30),  # Before start
        )
        
        with pytest.raises(ValidationError) as exc_info:
            academic_year.full_clean()
        
        assert "Enrollment period must be within academic year dates" in str(exc_info.value)


@pytest.mark.django_db
class TestEnrollmentStatusTransition:
    """Test transitioning to ENROLLMENT status with enrollment period."""
    
    def test_can_transition_to_enrollment_status(self, academic_year_with_enrollment_period):
        """Test moving to ENROLLMENT status when setup is complete."""
        # Complete setup first
        academic_year_with_enrollment_period.setup_completed = True
        academic_year_with_enrollment_period.status = AcademicYear.Status.ENROLLMENT
        academic_year_with_enrollment_period.save()
        
        academic_year_with_enrollment_period.full_clean()  # Should not raise
        assert academic_year_with_enrollment_period.status == AcademicYear.Status.ENROLLMENT
        assert academic_year_with_enrollment_period.is_in_enrollment is True
    
    def test_enrollment_status_requires_setup_completed(self, academic_year_with_enrollment_period):
        """Test that ENROLLMENT status requires setup_completed=True."""
        # Try to set ENROLLMENT without completing setup
        academic_year_with_enrollment_period.status = AcademicYear.Status.ENROLLMENT
        academic_year_with_enrollment_period.setup_completed = False
        
        with pytest.raises(ValidationError) as exc_info:
            academic_year_with_enrollment_period.full_clean()
        
        assert "setup_completed must be True" in str(exc_info.value)
    
    def test_can_accept_grades_during_enrollment(self, setup_completed_academic_year):
        """Test that grades can still be created during ENROLLMENT phase."""
        assert setup_completed_academic_year.status == AcademicYear.Status.ENROLLMENT
        assert setup_completed_academic_year.can_accept_grades() is True


@pytest.mark.django_db
class TestStudentEnrollmentDuringPeriod:
    """Test student enrollment during enrollment period."""
    
    def test_can_create_student_enrollment_during_enrollment_phase(
        self, 
        setup_completed_academic_year, 
        grade_for_enrollment_year, 
        student_user
    ):
        """Test that student enrollments can be created during ENROLLMENT phase."""
        # Verify we're in ENROLLMENT status
        assert setup_completed_academic_year.status == AcademicYear.Status.ENROLLMENT
        
        # Create enrollment
        enrollment = StudentEnrollment.objects.create(
            student=student_user,
            grade=grade_for_enrollment_year,
            academic_year=setup_completed_academic_year,
        )
        
        assert enrollment.pk is not None
        assert enrollment.student == student_user
        assert enrollment.grade == grade_for_enrollment_year
        assert enrollment.academic_year == setup_completed_academic_year
    
    def test_multiple_students_can_enroll(
        self,
        setup_completed_academic_year,
        grade_for_enrollment_year,
        student_users,
    ):
        """Test that multiple students can be enrolled."""
        enrollments = []
        for student in student_users:
            enrollment = StudentEnrollment.objects.create(
                student=student,
                grade=grade_for_enrollment_year,
                academic_year=setup_completed_academic_year,
            )
            enrollments.append(enrollment)
        
        assert len(enrollments) == len(student_users)
        assert setup_completed_academic_year.studentenrollment_set.count() == len(student_users)
    
    def test_student_can_only_enroll_once_per_academic_year(
        self,
        setup_completed_academic_year,
        grade_for_enrollment_year,
        student_user,
    ):
        """Test that a student can only be enrolled once per academic year."""
        # First enrollment
        StudentEnrollment.objects.create(
            student=student_user,
            grade=grade_for_enrollment_year,
            academic_year=setup_completed_academic_year,
        )
        
        # Create another grade
        another_grade = Grade.objects.create(
            name="Class 3A",
            grade="3",
            academic_year=setup_completed_academic_year,
        )
        
        # Try to enroll same student in different grade for same year
        with pytest.raises(Exception):  # IntegrityError
            StudentEnrollment.objects.create(
                student=student_user,
                grade=another_grade,
                academic_year=setup_completed_academic_year,
            )
    
    def test_student_can_enroll_in_different_academic_years(
        self,
        setup_completed_academic_year,
        grade_for_enrollment_year,
        student_user,
        base_date,
    ):
        """Test that a student can enroll in different academic years."""
        # Enroll in first year
        enrollment1 = StudentEnrollment.objects.create(
            student=student_user,
            grade=grade_for_enrollment_year,
            academic_year=setup_completed_academic_year,
        )
        
        # Create another academic year
        another_year = AcademicYear.objects.create(
            name="2027 / 2028",
            start_date=base_date + timedelta(days=365),
            end_date=base_date + timedelta(days=730),
            status=AcademicYear.Status.ENROLLMENT,
            setup_completed=True,
        )
        
        another_grade = Grade.objects.create(
            name="Class 3B",
            grade="3",
            academic_year=another_year,
        )
        
        # Enroll in second year (should succeed)
        enrollment2 = StudentEnrollment.objects.create(
            student=student_user,
            grade=another_grade,
            academic_year=another_year,
        )
        
        assert enrollment1.academic_year != enrollment2.academic_year
        assert student_user.student_grades.count() == 2


@pytest.mark.django_db
class TestEnrollmentPeriodEdgeCases:
    """Test edge cases for enrollment period configuration."""
    
    def test_very_short_enrollment_period(self, base_date):
        """Test enrollment period of just a few days."""
        academic_year = AcademicYear.objects.create(
            name="Short Enrollment",
            start_date=base_date,
            end_date=base_date + timedelta(days=365),
            enrollment_start_date=base_date,
            enrollment_end_date=base_date + timedelta(days=3),  # Just 3 days
        )
        
        academic_year.full_clean()  # Should not raise
        assert (academic_year.enrollment_end_date - academic_year.enrollment_start_date).days == 3
    
    def test_very_long_enrollment_period(self, base_date):
        """Test enrollment period spanning most of academic year."""
        academic_year = AcademicYear.objects.create(
            name="Long Enrollment",
            start_date=base_date,
            end_date=base_date + timedelta(days=365),
            enrollment_start_date=base_date,
            enrollment_end_date=base_date + timedelta(days=300),  # 300 days
        )
        
        academic_year.full_clean()  # Should not raise
        assert (academic_year.enrollment_end_date - academic_year.enrollment_start_date).days == 300
    
    def test_updating_enrollment_period_after_creation(self, academic_year_with_enrollment_period):
        """Test modifying enrollment period after academic year is created."""
        original_start = academic_year_with_enrollment_period.enrollment_start_date
        original_end = academic_year_with_enrollment_period.enrollment_end_date
        
        # Update enrollment period
        new_start = original_start + timedelta(days=5)
        new_end = original_end + timedelta(days=5)
        
        academic_year_with_enrollment_period.enrollment_start_date = new_start
        academic_year_with_enrollment_period.enrollment_end_date = new_end
        academic_year_with_enrollment_period.save()
        
        academic_year_with_enrollment_period.full_clean()  # Should not raise
        assert academic_year_with_enrollment_period.enrollment_start_date == new_start
        assert academic_year_with_enrollment_period.enrollment_end_date == new_end
    
    def test_removing_enrollment_period(self, academic_year_with_enrollment_period):
        """Test removing enrollment period by setting both dates to None."""
        academic_year_with_enrollment_period.enrollment_start_date = None
        academic_year_with_enrollment_period.enrollment_end_date = None
        academic_year_with_enrollment_period.save()
        
        academic_year_with_enrollment_period.full_clean()  # Should not raise
        assert academic_year_with_enrollment_period.enrollment_start_date is None
        assert academic_year_with_enrollment_period.enrollment_end_date is None
