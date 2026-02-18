"""
Test Use Case 5: Academic Year Activation

Real-World Scenario:
Year moves to ACTIVE status.

Expectations:
✔ System behavior:
  - Grade creation → ❌ Usually locked
  - StudentEnrollment → ❌ Typically frozen
  - Teaching / Attendance → ✅ Allowed
  - Assessments → ✅ Allowed
✔ Valid transitions:
  - ENROLLMENT -> ACTIVE
  - SETUP -> ACTIVE (for mid-year)
✔ Requirements:
  - setup_completed must be True
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
class TestActivationRequirements:
    """Test requirements for activating academic year."""
    
    def test_active_status_requires_setup_completed(self, academic_year_dates):
        """Test that ACTIVE status requires setup_completed=True."""
        academic_year = AcademicYear.objects.create(
            name="Active Year",
            start_date=academic_year_dates["start_date"],
            end_date=academic_year_dates["end_date"],
            status=AcademicYear.Status.ACTIVE,
            setup_completed=True,  # Required
        )
        
        academic_year.full_clean()  # Should not raise
        assert academic_year.status == AcademicYear.Status.ACTIVE
        assert academic_year.setup_completed is True
    
    def test_cannot_activate_without_setup_completed(self, academic_year_dates):
        """Test that cannot set ACTIVE status without setup_completed."""
        academic_year = AcademicYear(
            name="Invalid Active",
            start_date=academic_year_dates["start_date"],
            end_date=academic_year_dates["end_date"],
            status=AcademicYear.Status.ACTIVE,
            setup_completed=False,  # Invalid!
        )
        
        with pytest.raises(ValidationError) as exc_info:
            academic_year.full_clean()
        
        assert "setup_completed must be True" in str(exc_info.value)
    
    def test_active_year_is_considered_active(self, active_academic_year):
        """Test that ACTIVE status is considered an active year."""
        assert active_academic_year.status == AcademicYear.Status.ACTIVE
        assert active_academic_year.is_active_year is True


@pytest.mark.django_db
class TestTransitionToActive:
    """Test transitions to ACTIVE status."""
    
    def test_transition_from_enrollment_to_active(self, setup_completed_academic_year):
        """Test transitioning from ENROLLMENT to ACTIVE (typical path)."""
        # Verify we're in ENROLLMENT
        assert setup_completed_academic_year.status == AcademicYear.Status.ENROLLMENT
        assert setup_completed_academic_year.setup_completed is True
        
        # Transition to ACTIVE
        setup_completed_academic_year.status = AcademicYear.Status.ACTIVE
        setup_completed_academic_year.save()
        
        setup_completed_academic_year.full_clean()  # Should not raise
        assert setup_completed_academic_year.status == AcademicYear.Status.ACTIVE
    
    def test_transition_from_setup_to_active_for_mid_year(self, mid_year_dates):
        """Test transitioning from SETUP to ACTIVE for mid-year adoption."""
        academic_year = AcademicYear.objects.create(
            name="Mid-Year Activation",
            start_date=mid_year_dates["start_date"],
            end_date=mid_year_dates["end_date"],
            deployment_type=AcademicYear.DeploymentType.MID_YEAR,
            status=AcademicYear.Status.SETUP,
            setup_completed=False,
        )
        
        # Complete setup and activate
        academic_year.setup_completed = True
        academic_year.status = AcademicYear.Status.ACTIVE
        academic_year.save()
        
        academic_year.full_clean()  # Should not raise
        assert academic_year.status == AcademicYear.Status.ACTIVE
    
    def test_cannot_transition_from_setup_to_active_for_fresh_start_typically(self, fresh_start_academic_year):
        """
        Test that fresh start typically goes through ENROLLMENT before ACTIVE.
        
        Note: This is enforced by business logic, not model validation.
        The model allows it, but orchestrator should prevent it.
        """
        # Model allows this
        fresh_start_academic_year.setup_completed = True
        fresh_start_academic_year.status = AcademicYear.Status.ACTIVE
        fresh_start_academic_year.save()
        
        fresh_start_academic_year.full_clean()  # Model doesn't prevent this
        
        # But business logic (orchestrator) would typically require ENROLLMENT first
        assert fresh_start_academic_year.deployment_type == AcademicYear.DeploymentType.FRESH_START


@pytest.mark.django_db
class TestGradeCreationRestrictions:
    """Test that grade creation is typically locked during ACTIVE status."""
    
    def test_cannot_create_grades_when_active(self, active_academic_year):
        """Test that can_accept_grades returns False for ACTIVE status."""
        assert active_academic_year.status == AcademicYear.Status.ACTIVE
        assert active_academic_year.can_accept_grades() is False
    
    def test_grade_creation_policy_enforced(self, active_academic_year):
        """Test that Grade model checks academic year policy."""
        assert Grade.can_be_created_for_year(active_academic_year) is False
    
    def test_comparison_with_enrollment_status(self, setup_completed_academic_year):
        """Test that ENROLLMENT allows grade creation but ACTIVE does not."""
        # ENROLLMENT allows grades
        assert setup_completed_academic_year.status == AcademicYear.Status.ENROLLMENT
        assert setup_completed_academic_year.can_accept_grades() is True
        
        # Transition to ACTIVE
        setup_completed_academic_year.status = AcademicYear.Status.ACTIVE
        setup_completed_academic_year.save()
        
        # Now grades are locked
        assert setup_completed_academic_year.can_accept_grades() is False


@pytest.mark.django_db
class TestStudentEnrollmentDuringActive:
    """Test student enrollment behavior during ACTIVE status."""
    
    def test_can_technically_enroll_students_in_active(
        self,
        active_academic_year,
        student_user,
    ):
        """
        Test that model allows student enrollment during ACTIVE.
        
        Note: Business logic might restrict this, but model allows it
        for late enrollments or transfers.
        """
        # Create a grade (from before activation)
        grade = Grade.objects.create(
            name="Active Year Grade",
            grade="1",
            academic_year=active_academic_year,
        )
        
        # Enrollment is technically allowed at model level
        enrollment = StudentEnrollment.objects.create(
            student=student_user,
            grade=grade,
            academic_year=active_academic_year,
        )
        
        assert enrollment.pk is not None
        assert enrollment.academic_year.status == AcademicYear.Status.ACTIVE
    
    def test_late_enrollment_scenario(self, active_academic_year, student_user):
        """Test late enrollment scenario (student transfers mid-year)."""
        # In real world, a student might transfer to school mid-year
        grade = Grade.objects.create(
            name="Transfer Grade",
            grade="3",
            academic_year=active_academic_year,
        )
        
        # Late enrollment is allowed
        enrollment = StudentEnrollment.objects.create(
            student=student_user,
            grade=grade,
            academic_year=active_academic_year,
        )
        
        assert enrollment.pk is not None
        # Business logic would typically track this as late enrollment


@pytest.mark.django_db
class TestActiveYearOperations:
    """Test allowed and restricted operations during ACTIVE status."""
    
    def test_active_year_properties(self, active_academic_year):
        """Test properties of active academic year."""
        assert active_academic_year.status == AcademicYear.Status.ACTIVE
        assert active_academic_year.is_active_year is True
        assert active_academic_year.is_in_setup is False
        assert active_academic_year.is_in_enrollment is False
    
    def test_can_update_academic_year_details(self, active_academic_year):
        """Test that academic year details can be updated when active."""
        original_name = active_academic_year.name
        active_academic_year.name = "Updated Active Year"
        active_academic_year.save()
        
        active_academic_year.refresh_from_db()
        assert active_academic_year.name == "Updated Active Year"
        assert active_academic_year.name != original_name
    
    def test_existing_grades_remain_accessible(self, grade_for_active_year):
        """Test that existing grades remain accessible during ACTIVE."""
        assert grade_for_active_year.academic_year.status == AcademicYear.Status.ACTIVE
        assert grade_for_active_year.is_active is True
        
        # Can query and access
        grade = Grade.objects.get(pk=grade_for_active_year.pk)
        assert grade.academic_year.status == AcademicYear.Status.ACTIVE
    
    def test_can_modify_existing_grades(self, grade_for_active_year):
        """Test that existing grades can be modified during ACTIVE."""
        original_description = grade_for_active_year.description
        grade_for_active_year.description = "Updated description during active year"
        grade_for_active_year.save()
        
        grade_for_active_year.refresh_from_db()
        assert grade_for_active_year.description != original_description


@pytest.mark.django_db
class TestActivationEdgeCases:
    """Test edge cases for academic year activation."""
    
    def test_can_have_multiple_active_years(self, active_academic_year, academic_year_dates):
        """Test that system can have multiple active academic years."""
        # Create another active year (different dates)
        another_active = AcademicYear.objects.create(
            name="Another Active Year",
            start_date=academic_year_dates["start_date"],
            end_date=academic_year_dates["end_date"],
            status=AcademicYear.Status.ACTIVE,
            setup_completed=True,
        )
        
        # Both should be valid
        assert active_academic_year.status == AcademicYear.Status.ACTIVE
        assert another_active.status == AcademicYear.Status.ACTIVE
        assert AcademicYear.objects.filter(status=AcademicYear.Status.ACTIVE).count() == 2
    
    def test_reactivating_from_completed_not_typically_allowed(self, academic_year_dates):
        """
        Test that moving from COMPLETED back to ACTIVE is technically possible
        but would be unusual.
        """
        academic_year = AcademicYear.objects.create(
            name="Completed Year",
            start_date=academic_year_dates["start_date"] - timedelta(days=730),
            end_date=academic_year_dates["start_date"] - timedelta(days=365),
            status=AcademicYear.Status.COMPLETED,
            setup_completed=True,
        )
        
        # Model allows going back to ACTIVE
        academic_year.status = AcademicYear.Status.ACTIVE
        academic_year.save()
        
        academic_year.full_clean()  # Model doesn't prevent this
        # But business logic would typically not allow this
    
    def test_cannot_skip_from_active_to_setup(self, active_academic_year):
        """Test that cannot revert from ACTIVE to SETUP."""
        active_academic_year.status = AcademicYear.Status.SETUP
        # setup_completed is True, which is invalid for SETUP
        
        with pytest.raises(ValidationError) as exc_info:
            active_academic_year.full_clean()
        
        assert "Cannot be in SETUP status when setup is already completed" in str(exc_info.value)


@pytest.mark.django_db
class TestActiveStatusValidation:
    """Test validation specific to ACTIVE status."""
    
    def test_active_year_created_with_valid_dates(self, academic_year_dates):
        """Test creating active year with valid date range."""
        academic_year = AcademicYear.objects.create(
            name="Valid Active Year",
            start_date=academic_year_dates["start_date"],
            end_date=academic_year_dates["end_date"],
            status=AcademicYear.Status.ACTIVE,
            setup_completed=True,
        )
        
        academic_year.full_clean()
        assert academic_year.start_date < academic_year.end_date
    
    def test_active_year_with_enrollment_period(self, academic_year_dates):
        """Test active year can have enrollment period defined (historical)."""
        academic_year = AcademicYear.objects.create(
            name="Active with Enrollment Dates",
            start_date=academic_year_dates["start_date"],
            end_date=academic_year_dates["end_date"],
            status=AcademicYear.Status.ACTIVE,
            setup_completed=True,
            enrollment_start_date=academic_year_dates["enrollment_start_date"],
            enrollment_end_date=academic_year_dates["enrollment_end_date"],
        )
        
        academic_year.full_clean()  # Should not raise
        # Enrollment dates are historical record of when enrollment happened
    
    def test_active_year_without_enrollment_period(self, academic_year_dates):
        """Test active year without enrollment period (mid-year scenario)."""
        academic_year = AcademicYear.objects.create(
            name="Active No Enrollment",
            start_date=academic_year_dates["start_date"],
            end_date=academic_year_dates["end_date"],
            deployment_type=AcademicYear.DeploymentType.MID_YEAR,
            status=AcademicYear.Status.ACTIVE,
            setup_completed=True,
            enrollment_start_date=None,
            enrollment_end_date=None,
        )
        
        academic_year.full_clean()  # Should not raise


@pytest.mark.django_db
class TestActiveYearQuerying:
    """Test querying for active academic years."""
    
    def test_filter_active_years(self, active_academic_year, completed_academic_year):
        """Test filtering for ACTIVE status years."""
        active_years = AcademicYear.objects.filter(status=AcademicYear.Status.ACTIVE)
        
        assert active_academic_year in active_years
        assert completed_academic_year not in active_years
    
    def test_is_active_year_property_includes_multiple_statuses(
        self,
        fresh_start_academic_year,
        setup_completed_academic_year,
        active_academic_year,
    ):
        """Test that is_active_year includes SETUP, ENROLLMENT, and ACTIVE."""
        # SETUP, ENROLLMENT, and ACTIVE are all considered "active years"
        assert fresh_start_academic_year.is_active_year is True
        assert setup_completed_academic_year.is_active_year is True
        assert active_academic_year.is_active_year is True
    
    def test_get_current_active_teaching_year(self, active_academic_year, setup_completed_academic_year):
        """Test getting the current year for teaching activities."""
        # In a real system, you'd filter by ACTIVE status and current date
        teaching_years = AcademicYear.objects.filter(status=AcademicYear.Status.ACTIVE)
        
        assert active_academic_year in teaching_years
        assert setup_completed_academic_year not in teaching_years  # Still in ENROLLMENT


@pytest.mark.django_db
class TestRealWorldActivationScenarios:
    """Test real-world activation scenarios."""
    
    def test_fresh_start_full_lifecycle(self, academic_year_dates):
        """Test complete lifecycle: SETUP -> ENROLLMENT -> ACTIVE."""
        # Create in SETUP
        academic_year = AcademicYear.objects.create(
            name="Full Lifecycle",
            start_date=academic_year_dates["start_date"],
            end_date=academic_year_dates["end_date"],
            deployment_type=AcademicYear.DeploymentType.FRESH_START,
            enrollment_start_date=academic_year_dates["enrollment_start_date"],
            enrollment_end_date=academic_year_dates["enrollment_end_date"],
            status=AcademicYear.Status.SETUP,
            setup_completed=False,
        )
        
        # Phase 1: Setup - create grades
        grade = Grade.objects.create(
            name="Setup Grade",
            grade="1",
            academic_year=academic_year,
        )
        assert academic_year.can_accept_grades() is True
        
        # Phase 2: Move to ENROLLMENT
        academic_year.setup_completed = True
        academic_year.status = AcademicYear.Status.ENROLLMENT
        academic_year.save()
        assert academic_year.can_accept_grades() is True  # Still can create grades
        
        # Phase 3: Enroll students
        student = User.objects.create_user(username="student_lifecycle", email="student@test.com")
        StudentEnrollment.objects.create(
            student=student,
            grade=grade,
            academic_year=academic_year,
        )
        
        # Phase 4: Activate
        academic_year.status = AcademicYear.Status.ACTIVE
        academic_year.save()
        academic_year.full_clean()
        
        # Verify final state
        assert academic_year.status == AcademicYear.Status.ACTIVE
        assert academic_year.can_accept_grades() is False  # Now locked
        assert academic_year.grades.count() == 1
        assert academic_year.studentenrollment_set.count() == 1
    
    def test_mid_year_adoption_activation(self, mid_year_dates):
        """Test mid-year adoption: SETUP -> ACTIVE (skip ENROLLMENT)."""
        # Create in SETUP
        academic_year = AcademicYear.objects.create(
            name="Mid-Year Activation",
            start_date=mid_year_dates["start_date"],
            end_date=mid_year_dates["end_date"],
            deployment_type=AcademicYear.DeploymentType.MID_YEAR,
            status=AcademicYear.Status.SETUP,
            setup_completed=False,
        )
        
        # Setup: Import existing grades and students
        grade = Grade.objects.create(
            name="Imported Grade",
            grade="2",
            academic_year=academic_year,
        )
        
        # Activate directly (skip ENROLLMENT)
        academic_year.setup_completed = True
        academic_year.status = AcademicYear.Status.ACTIVE
        academic_year.save()
        academic_year.full_clean()
        
        # Verify
        assert academic_year.status == AcademicYear.Status.ACTIVE
        assert academic_year.deployment_type == AcademicYear.DeploymentType.MID_YEAR
        assert academic_year.enrollment_start_date is None  # No enrollment period


# Import User model
from django.contrib.auth import get_user_model
User = get_user_model()
