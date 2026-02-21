"""
Test Use Case 4: Mid-Year Adoption

Real-World Scenario:
School joins platform mid-semester:
- Deployment → MID_YEAR
- Status → ACTIVE (typically, not ENROLLMENT)
- Enrollment period → Often null (not applicable)

Expectations:
✔ Valid:
  - Enrollment period can be null
  - Can start directly in ACTIVE status (after setup)
  - No enrollment phase required
✘ Invalid:
  - deployment_type = MID_YEAR AND status = ENROLLMENT
  - Expectation: Raise "Mid-year adoption should not have an enrollment phase."
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
class TestMidYearAdoptionCreation:
    """Test creating a mid-year adoption academic year."""
    
    def test_create_mid_year_adoption_without_enrollment_period(self, mid_year_dates):
        """Test creating mid-year adoption without enrollment period."""
        academic_year = AcademicYear.objects.create(
            name="2027 Mid-Year",
            start_date=mid_year_dates["start_date"],
            end_date=mid_year_dates["end_date"],
            deployment_type=AcademicYear.DeploymentType.MID_YEAR,
            status=AcademicYear.Status.ACTIVE,
            setup_completed=True,
            # No enrollment period
            enrollment_start_date=None,
            enrollment_end_date=None,
        )
        
        academic_year.full_clean()  # Should not raise
        assert academic_year.deployment_type == AcademicYear.DeploymentType.MID_YEAR
        assert academic_year.status == AcademicYear.Status.ACTIVE
        assert academic_year.enrollment_start_date is None
        assert academic_year.enrollment_end_date is None
    
    def test_mid_year_can_have_null_enrollment_dates(self, mid_year_dates):
        """Test that mid-year adoption can have null enrollment dates."""
        academic_year = AcademicYear.objects.create(
            name="Mid-Year No Enrollment",
            start_date=mid_year_dates["start_date"],
            end_date=mid_year_dates["end_date"],
            deployment_type=AcademicYear.DeploymentType.MID_YEAR,
            status=AcademicYear.Status.ACTIVE,
            setup_completed=True,
        )
        
        assert academic_year.enrollment_start_date is None
        assert academic_year.enrollment_end_date is None
        academic_year.full_clean()  # Should not raise
    
    def test_mid_year_starts_in_setup_status(self, mid_year_dates):
        """Test that mid-year adoption can start in SETUP status."""
        academic_year = AcademicYear.objects.create(
            name="Mid-Year Setup",
            start_date=mid_year_dates["start_date"],
            end_date=mid_year_dates["end_date"],
            deployment_type=AcademicYear.DeploymentType.MID_YEAR,
            status=AcademicYear.Status.SETUP,
            setup_completed=False,
        )
        
        academic_year.full_clean()  # Should not raise
        assert academic_year.status == AcademicYear.Status.SETUP
    
    def test_mid_year_transitions_setup_to_active(self, mid_year_dates):
        """Test mid-year adoption can transition from SETUP to ACTIVE."""
        academic_year = AcademicYear.objects.create(
            name="Mid-Year Transition",
            start_date=mid_year_dates["start_date"],
            end_date=mid_year_dates["end_date"],
            deployment_type=AcademicYear.DeploymentType.MID_YEAR,
            status=AcademicYear.Status.SETUP,
            setup_completed=False,
        )
        
        # Transition to ACTIVE (skip ENROLLMENT)
        academic_year.setup_completed = True
        academic_year.status = AcademicYear.Status.ACTIVE
        academic_year.save()
        
        academic_year.full_clean()  # Should not raise
        assert academic_year.status == AcademicYear.Status.ACTIVE


@pytest.mark.django_db
class TestMidYearEnrollmentPhaseRestriction:
    """Test that mid-year adoption cannot have ENROLLMENT status."""
    
    def test_mid_year_cannot_be_in_enrollment_status(self, mid_year_dates):
        """Test that mid-year adoption cannot have ENROLLMENT status."""
        academic_year = AcademicYear(
            name="Invalid Mid-Year Enrollment",
            start_date=mid_year_dates["start_date"],
            end_date=mid_year_dates["end_date"],
            deployment_type=AcademicYear.DeploymentType.MID_YEAR,
            status=AcademicYear.Status.ENROLLMENT,  # Invalid!
            setup_completed=True,
        )
        
        with pytest.raises(ValidationError) as exc_info:
            academic_year.full_clean()
        
        assert "Mid-year adoption should not have an enrollment phase" in str(exc_info.value)
    
    def test_mid_year_enrollment_status_rejected_even_with_dates(self, mid_year_dates):
        """Test mid-year with enrollment dates still cannot be in ENROLLMENT status."""
        academic_year = AcademicYear(
            name="Mid-Year Invalid Enrollment",
            start_date=mid_year_dates["start_date"],
            end_date=mid_year_dates["end_date"],
            deployment_type=AcademicYear.DeploymentType.MID_YEAR,
            status=AcademicYear.Status.ENROLLMENT,  # Invalid!
            setup_completed=True,
            enrollment_start_date=mid_year_dates["start_date"],
            enrollment_end_date=mid_year_dates["start_date"] + timedelta(days=15),
        )
        
        with pytest.raises(ValidationError) as exc_info:
            academic_year.full_clean()
        
        assert "Mid-year adoption should not have an enrollment phase" in str(exc_info.value)
    
    def test_cannot_transition_mid_year_to_enrollment(self, mid_year_academic_year):
        """Test that cannot transition mid-year from ACTIVE to ENROLLMENT."""
        assert mid_year_academic_year.deployment_type == AcademicYear.DeploymentType.MID_YEAR
        
        # Try to change to ENROLLMENT
        mid_year_academic_year.status = AcademicYear.Status.ENROLLMENT
        
        with pytest.raises(ValidationError) as exc_info:
            mid_year_academic_year.full_clean()
        
        assert "Mid-year adoption should not have an enrollment phase" in str(exc_info.value)


@pytest.mark.django_db
class TestMidYearWithEnrollmentPeriod:
    """Test mid-year adoption with enrollment period (edge case)."""
    
    def test_mid_year_can_have_enrollment_dates_if_not_in_enrollment_status(self, mid_year_dates):
        """Test mid-year can have enrollment dates as long as status is not ENROLLMENT."""
        # This might be used for tracking when students were onboarded
        academic_year = AcademicYear.objects.create(
            name="Mid-Year With Dates",
            start_date=mid_year_dates["start_date"],
            end_date=mid_year_dates["end_date"],
            deployment_type=AcademicYear.DeploymentType.MID_YEAR,
            status=AcademicYear.Status.ACTIVE,  # ACTIVE, not ENROLLMENT
            setup_completed=True,
            enrollment_start_date=mid_year_dates["start_date"],
            enrollment_end_date=mid_year_dates["start_date"] + timedelta(days=30),
        )
        
        academic_year.full_clean()  # Should not raise
        assert academic_year.enrollment_start_date is not None
        assert academic_year.status != AcademicYear.Status.ENROLLMENT


@pytest.mark.django_db
class TestMidYearOperations:
    """Test operations allowed for mid-year adoption."""
    
    def test_can_create_grades_for_mid_year_in_setup(self, mid_year_dates):
        """Test that grades can be created for mid-year during setup."""
        academic_year = AcademicYear.objects.create(
            name="Mid-Year Grades Setup",
            start_date=mid_year_dates["start_date"],
            end_date=mid_year_dates["end_date"],
            deployment_type=AcademicYear.DeploymentType.MID_YEAR,
            status=AcademicYear.Status.SETUP,
            setup_completed=False,
        )
        
        assert academic_year.can_accept_grades() is True
        
        grade = Grade.objects.create(
            name="Mid-Year Class 1A",
            grade="1",
            academic_year=academic_year,
        )
        
        assert grade.pk is not None
    
    def test_cannot_create_grades_for_active_mid_year(self, mid_year_academic_year):
        """Test that grades cannot be created for ACTIVE mid-year."""
        assert mid_year_academic_year.status == AcademicYear.Status.ACTIVE
        assert mid_year_academic_year.can_accept_grades() is False
    
    def test_can_enroll_students_in_active_mid_year(
        self,
        mid_year_academic_year,
        student_user,
    ):
        """Test that students can be enrolled in active mid-year (pre-existing)."""
        # Grades must be created before moving to ACTIVE (during SETUP phase)
        mid_year_academic_year.status = AcademicYear.Status.SETUP
        mid_year_academic_year.setup_completed = False
        mid_year_academic_year.save()
        
        # Create a grade during SETUP (would have been created during setup)
        grade = Grade.objects.create(
            name="Mid-Year Active Grade",
            grade="1",
            academic_year=mid_year_academic_year,
        )
        
        # Now transition to ACTIVE
        mid_year_academic_year.setup_completed = True
        mid_year_academic_year.status = AcademicYear.Status.ACTIVE
        mid_year_academic_year.save()
        
        # This tests that enrollment can happen in ACTIVE status
        enrollment = StudentEnrollment.objects.create(
            student=student_user,
            grade=grade,
            academic_year=mid_year_academic_year,
        )
        
        assert enrollment.pk is not None
        assert enrollment.academic_year.deployment_type == AcademicYear.DeploymentType.MID_YEAR


@pytest.mark.django_db
class TestMidYearVsFreshStartComparison:
    """Test differences between mid-year and fresh start deployments."""
    
    def test_fresh_start_allows_enrollment_status(self, academic_year_dates):
        """Test that fresh start can have ENROLLMENT status."""
        academic_year = AcademicYear.objects.create(
            name="Fresh Start Enrollment",
            start_date=academic_year_dates["start_date"],
            end_date=academic_year_dates["end_date"],
            deployment_type=AcademicYear.DeploymentType.FRESH_START,
            status=AcademicYear.Status.ENROLLMENT,
            setup_completed=True,
        )
        
        academic_year.full_clean()  # Should not raise
        assert academic_year.deployment_type == AcademicYear.DeploymentType.FRESH_START
        assert academic_year.status == AcademicYear.Status.ENROLLMENT
    
    def test_mid_year_rejects_enrollment_status(self, mid_year_dates):
        """Test that mid-year rejects ENROLLMENT status."""
        academic_year = AcademicYear(
            name="Mid-Year Enrollment Rejected",
            start_date=mid_year_dates["start_date"],
            end_date=mid_year_dates["end_date"],
            deployment_type=AcademicYear.DeploymentType.MID_YEAR,
            status=AcademicYear.Status.ENROLLMENT,
            setup_completed=True,
        )
        
        with pytest.raises(ValidationError) as exc_info:
            academic_year.full_clean()
        
        assert "Mid-year adoption should not have an enrollment phase" in str(exc_info.value)
    
    def test_fresh_start_typical_flow(self, academic_year_dates):
        """Test typical fresh start flow: SETUP -> ENROLLMENT -> ACTIVE."""
        academic_year = AcademicYear.objects.create(
            name="Fresh Start Flow",
            start_date=academic_year_dates["start_date"],
            end_date=academic_year_dates["end_date"],
            deployment_type=AcademicYear.DeploymentType.FRESH_START,
            status=AcademicYear.Status.SETUP,
            setup_completed=False,
        )
        
        # SETUP -> ENROLLMENT
        academic_year.setup_completed = True
        academic_year.status = AcademicYear.Status.ENROLLMENT
        academic_year.save()
        academic_year.full_clean()
        
        # ENROLLMENT -> ACTIVE
        academic_year.status = AcademicYear.Status.ACTIVE
        academic_year.save()
        academic_year.full_clean()
        
        assert academic_year.status == AcademicYear.Status.ACTIVE
    
    def test_mid_year_typical_flow(self, mid_year_dates):
        """Test typical mid-year flow: SETUP -> ACTIVE (skip ENROLLMENT)."""
        academic_year = AcademicYear.objects.create(
            name="Mid-Year Flow",
            start_date=mid_year_dates["start_date"],
            end_date=mid_year_dates["end_date"],
            deployment_type=AcademicYear.DeploymentType.MID_YEAR,
            status=AcademicYear.Status.SETUP,
            setup_completed=False,
        )
        
        # SETUP -> ACTIVE (skip ENROLLMENT)
        academic_year.setup_completed = True
        academic_year.status = AcademicYear.Status.ACTIVE
        academic_year.save()
        academic_year.full_clean()
        
        assert academic_year.status == AcademicYear.Status.ACTIVE


@pytest.mark.django_db
class TestMidYearStatusTransitions:
    """Test all valid status transitions for mid-year adoption."""
    
    def test_mid_year_setup_to_active_is_valid(self, mid_year_dates):
        """Test SETUP -> ACTIVE transition for mid-year."""
        academic_year = AcademicYear.objects.create(
            name="Mid-Year Setup to Active",
            start_date=mid_year_dates["start_date"],
            end_date=mid_year_dates["end_date"],
            deployment_type=AcademicYear.DeploymentType.MID_YEAR,
            status=AcademicYear.Status.SETUP,
            setup_completed=False,
        )
        
        academic_year.setup_completed = True
        academic_year.status = AcademicYear.Status.ACTIVE
        academic_year.save()
        
        academic_year.full_clean()  # Should not raise
    
    def test_mid_year_active_to_completed_is_valid(self, mid_year_academic_year):
        """Test ACTIVE -> COMPLETED transition for mid-year."""
        assert mid_year_academic_year.status == AcademicYear.Status.ACTIVE
        
        mid_year_academic_year.status = AcademicYear.Status.COMPLETED
        mid_year_academic_year.save()
        
        mid_year_academic_year.full_clean()  # Should not raise
        assert mid_year_academic_year.status == AcademicYear.Status.COMPLETED
    
    def test_mid_year_all_statuses_except_enrollment(self, mid_year_dates):
        """Test that mid-year can use all statuses except ENROLLMENT."""
        # Test SETUP
        year_setup = AcademicYear.objects.create(
            name="Mid-Year SETUP",
            start_date=mid_year_dates["start_date"],
            end_date=mid_year_dates["end_date"],
            deployment_type=AcademicYear.DeploymentType.MID_YEAR,
            status=AcademicYear.Status.SETUP,
            setup_completed=False,
        )
        year_setup.full_clean()
        
        # Test ACTIVE
        year_active = AcademicYear.objects.create(
            name="Mid-Year ACTIVE",
            start_date=mid_year_dates["start_date"] + timedelta(days=1),
            end_date=mid_year_dates["end_date"] + timedelta(days=1),
            deployment_type=AcademicYear.DeploymentType.MID_YEAR,
            status=AcademicYear.Status.ACTIVE,
            setup_completed=True,
        )
        year_active.full_clean()
        
        # Test COMPLETED
        year_completed = AcademicYear.objects.create(
            name="Mid-Year COMPLETED",
            start_date=mid_year_dates["start_date"] + timedelta(days=2),
            end_date=mid_year_dates["end_date"] + timedelta(days=2),
            deployment_type=AcademicYear.DeploymentType.MID_YEAR,
            status=AcademicYear.Status.COMPLETED,
            setup_completed=True,
        )
        year_completed.full_clean()
        
        # ENROLLMENT should fail
        with pytest.raises(ValidationError):
            year_enrollment = AcademicYear(
                name="Mid-Year ENROLLMENT",
                start_date=mid_year_dates["start_date"] + timedelta(days=3),
                end_date=mid_year_dates["end_date"] + timedelta(days=3),
                deployment_type=AcademicYear.DeploymentType.MID_YEAR,
                status=AcademicYear.Status.ENROLLMENT,
                setup_completed=True,
            )
            year_enrollment.full_clean()


@pytest.mark.django_db
class TestMidYearRealWorldScenarios:
    """Test real-world mid-year adoption scenarios."""
    
    def test_school_joins_mid_semester_scenario(self, mid_year_dates):
        """
        Test realistic scenario: School joins in January mid-semester.
        
        - Students already enrolled elsewhere
        - Classes already in progress
        - Need to import existing data
        - Go directly to ACTIVE status
        """
        academic_year = AcademicYear.objects.create(
            name="Spring 2027 Mid-Year",
            start_date=mid_year_dates["start_date"],  # January 15
            end_date=mid_year_dates["end_date"],  # June 30 (end of semester)
            deployment_type=AcademicYear.DeploymentType.MID_YEAR,
            status=AcademicYear.Status.ACTIVE,
            setup_completed=True,
            # No enrollment period - students are already enrolled
            enrollment_start_date=None,
            enrollment_end_date=None,
        )
        
        academic_year.full_clean()
        
        # Verify characteristics
        assert academic_year.deployment_type == AcademicYear.DeploymentType.MID_YEAR
        assert academic_year.status == AcademicYear.Status.ACTIVE
        assert academic_year.enrollment_start_date is None
        assert academic_year.can_accept_grades() is False  # Classes already defined
    
    def test_mid_year_shorter_duration(self, base_date):
        """Test mid-year adoption with shorter duration (rest of semester)."""
        mid_year_start = base_date
        # Only 5 months left in academic year
        mid_year_end = base_date + timedelta(days=150)
        
        academic_year = AcademicYear.objects.create(
            name="Short Mid-Year",
            start_date=mid_year_start,
            end_date=mid_year_end,
            deployment_type=AcademicYear.DeploymentType.MID_YEAR,
            status=AcademicYear.Status.ACTIVE,
            setup_completed=True,
        )
        
        academic_year.full_clean()
        
        # Verify it's a valid but shorter academic year
        duration = (academic_year.end_date - academic_year.start_date).days
        assert duration == 150
        assert duration < 365  # Shorter than full year
