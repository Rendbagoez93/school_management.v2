"""
Test Use Case 3: Setup Completion Flow

Real-World Scenario:
School finishes configuration:
- Grades defined
- Subjects assigned (future feature)
- Curriculum mapped (future feature)

Admin sets:
- setup_completed = True
- status = ENROLLMENT or ACTIVE

Expectations:
✔ Valid only when: status != SETUP AND setup_completed = True
✔ System behavior:
  - Enrollment → Allowed
  - Teaching activities → Depends on status
✘ Invalid cases:
  - setup_completed = True while status = SETUP
  - status != SETUP while setup_completed = False
"""

import pytest
from django.core.exceptions import ValidationError

from applications.school_management.academic_management.models import (
    AcademicYear,
    StudentEnrollment,
)
from applications.school_management.grade_management.models import Grade


@pytest.mark.django_db
class TestSetupCompletionValidation:
    """Test validation rules for setup completion."""
    
    def test_setup_completed_with_enrollment_status_is_valid(self, academic_year_dates):
        """Test that setup_completed=True with ENROLLMENT status is valid."""
        academic_year = AcademicYear.objects.create(
            name="Setup Complete - Enrollment",
            start_date=academic_year_dates["start_date"],
            end_date=academic_year_dates["end_date"],
            status=AcademicYear.Status.ENROLLMENT,
            setup_completed=True,
        )
        
        academic_year.full_clean()  # Should not raise
        assert academic_year.setup_completed is True
        assert academic_year.status == AcademicYear.Status.ENROLLMENT
    
    def test_setup_completed_with_active_status_is_valid(self, academic_year_dates):
        """Test that setup_completed=True with ACTIVE status is valid."""
        academic_year = AcademicYear.objects.create(
            name="Setup Complete - Active",
            start_date=academic_year_dates["start_date"],
            end_date=academic_year_dates["end_date"],
            status=AcademicYear.Status.ACTIVE,
            setup_completed=True,
        )
        
        academic_year.full_clean()  # Should not raise
        assert academic_year.setup_completed is True
        assert academic_year.status == AcademicYear.Status.ACTIVE
    
    def test_setup_completed_with_completed_status_is_valid(self, academic_year_dates):
        """Test that setup_completed=True with COMPLETED status is valid."""
        academic_year = AcademicYear.objects.create(
            name="Setup Complete - Completed",
            start_date=academic_year_dates["start_date"],
            end_date=academic_year_dates["end_date"],
            status=AcademicYear.Status.COMPLETED,
            setup_completed=True,
        )
        
        academic_year.full_clean()  # Should not raise
        assert academic_year.setup_completed is True
        assert academic_year.status == AcademicYear.Status.COMPLETED
    
    def test_cannot_have_setup_completed_true_with_setup_status(self, academic_year_dates):
        """Test that setup_completed=True is invalid when status=SETUP."""
        academic_year = AcademicYear(
            name="Invalid Setup Complete",
            start_date=academic_year_dates["start_date"],
            end_date=academic_year_dates["end_date"],
            status=AcademicYear.Status.SETUP,
            setup_completed=True,  # Invalid!
        )
        
        with pytest.raises(ValidationError) as exc_info:
            academic_year.full_clean()
        
        assert "Cannot be in SETUP status when setup is already completed" in str(exc_info.value)
    
    def test_cannot_have_non_setup_status_without_completion(self, academic_year_dates):
        """Test that non-SETUP status requires setup_completed=True."""
        academic_year = AcademicYear(
            name="Invalid Enrollment",
            start_date=academic_year_dates["start_date"],
            end_date=academic_year_dates["end_date"],
            status=AcademicYear.Status.ENROLLMENT,
            setup_completed=False,  # Invalid!
        )
        
        with pytest.raises(ValidationError) as exc_info:
            academic_year.full_clean()
        
        assert "setup_completed must be True when status is not SETUP" in str(exc_info.value)
    
    def test_cannot_activate_without_setup_completed(self, academic_year_dates):
        """Test that ACTIVE status requires setup_completed=True."""
        academic_year = AcademicYear(
            name="Invalid Active",
            start_date=academic_year_dates["start_date"],
            end_date=academic_year_dates["end_date"],
            status=AcademicYear.Status.ACTIVE,
            setup_completed=False,  # Invalid!
        )
        
        with pytest.raises(ValidationError) as exc_info:
            academic_year.full_clean()
        
        assert "setup_completed must be True when status is not SETUP" in str(exc_info.value)
    
    def test_setup_status_must_have_setup_completed_false(self, fresh_start_academic_year):
        """Test that SETUP status must have setup_completed=False."""
        # Fresh start should be in SETUP with setup_completed=False
        assert fresh_start_academic_year.status == AcademicYear.Status.SETUP
        assert fresh_start_academic_year.setup_completed is False
        
        fresh_start_academic_year.full_clean()  # Should not raise


@pytest.mark.django_db
class TestSetupToEnrollmentTransition:
    """Test transitioning from SETUP to ENROLLMENT status."""
    
    def test_can_transition_from_setup_to_enrollment(self, fresh_start_academic_year):
        """Test transitioning from SETUP to ENROLLMENT after completion."""
        # Verify initial state
        assert fresh_start_academic_year.status == AcademicYear.Status.SETUP
        assert fresh_start_academic_year.setup_completed is False
        
        # Complete setup and transition
        fresh_start_academic_year.setup_completed = True
        fresh_start_academic_year.status = AcademicYear.Status.ENROLLMENT
        fresh_start_academic_year.save()
        
        fresh_start_academic_year.full_clean()  # Should not raise
        assert fresh_start_academic_year.status == AcademicYear.Status.ENROLLMENT
        assert fresh_start_academic_year.setup_completed is True
    
    def test_transition_requires_both_fields_updated(self, fresh_start_academic_year):
        """Test that both status and setup_completed must be updated together."""
        # Try to change status without setting setup_completed
        fresh_start_academic_year.status = AcademicYear.Status.ENROLLMENT
        # setup_completed is still False
        
        with pytest.raises(ValidationError) as exc_info:
            fresh_start_academic_year.full_clean()
        
        assert "setup_completed must be True" in str(exc_info.value)


@pytest.mark.django_db
class TestSetupToActiveTransition:
    """Test transitioning from SETUP to ACTIVE status (for mid-year)."""
    
    def test_can_transition_from_setup_to_active_for_mid_year(self, mid_year_dates):
        """Test mid-year adoption can go directly from SETUP to ACTIVE."""
        academic_year = AcademicYear.objects.create(
            name="Mid-Year Direct Active",
            start_date=mid_year_dates["start_date"],
            end_date=mid_year_dates["end_date"],
            deployment_type=AcademicYear.DeploymentType.MID_YEAR,
            status=AcademicYear.Status.SETUP,
            setup_completed=False,
        )
        
        # Transition to ACTIVE (skip ENROLLMENT for mid-year)
        academic_year.setup_completed = True
        academic_year.status = AcademicYear.Status.ACTIVE
        academic_year.save()
        
        academic_year.full_clean()  # Should not raise
        assert academic_year.status == AcademicYear.Status.ACTIVE
        assert academic_year.deployment_type == AcademicYear.DeploymentType.MID_YEAR


@pytest.mark.django_db
class TestOperationsAfterSetupCompletion:
    """Test allowed operations after setup is completed."""
    
    def test_enrollment_allowed_after_setup_completion(
        self,
        setup_completed_academic_year,
        grade_for_enrollment_year,
        student_user,
    ):
        """Test that student enrollment is allowed after setup completion."""
        assert setup_completed_academic_year.setup_completed is True
        assert setup_completed_academic_year.status == AcademicYear.Status.ENROLLMENT
        
        # Create enrollment
        enrollment = StudentEnrollment.objects.create(
            student=student_user,
            grade=grade_for_enrollment_year,
            academic_year=setup_completed_academic_year,
        )
        
        assert enrollment.pk is not None
    
    def test_grades_can_still_be_created_during_enrollment(self, setup_completed_academic_year):
        """Test that grades can be created even after setup completion during ENROLLMENT."""
        assert setup_completed_academic_year.status == AcademicYear.Status.ENROLLMENT
        assert setup_completed_academic_year.can_accept_grades() is True
        
        grade = Grade.objects.create(
            name="Late Grade",
            grade="5",
            academic_year=setup_completed_academic_year,
        )
        
        assert grade.pk is not None
    
    def test_can_update_academic_year_details_after_setup(self, setup_completed_academic_year):
        """Test that academic year can be updated after setup completion."""
        # Should be able to update fields like enrollment dates
        new_enrollment_start = setup_completed_academic_year.enrollment_start_date
        setup_completed_academic_year.name = "Updated Name"
        setup_completed_academic_year.save()
        
        setup_completed_academic_year.refresh_from_db()
        assert setup_completed_academic_year.name == "Updated Name"


@pytest.mark.django_db
class TestSetupNotCompletedRestrictions:
    """Test restrictions when setup is not completed."""
    
    def test_cannot_move_to_enrollment_without_completion(self, fresh_start_academic_year):
        """Test that cannot move to ENROLLMENT without completing setup."""
        fresh_start_academic_year.status = AcademicYear.Status.ENROLLMENT
        # setup_completed is still False
        
        with pytest.raises(ValidationError) as exc_info:
            fresh_start_academic_year.full_clean()
        
        assert "setup_completed must be True" in str(exc_info.value)
    
    def test_cannot_move_to_active_without_completion(self, fresh_start_academic_year):
        """Test that cannot move to ACTIVE without completing setup."""
        fresh_start_academic_year.status = AcademicYear.Status.ACTIVE
        # setup_completed is still False
        
        with pytest.raises(ValidationError) as exc_info:
            fresh_start_academic_year.full_clean()
        
        assert "setup_completed must be True" in str(exc_info.value)
    
    def test_cannot_complete_year_without_setup(self, fresh_start_academic_year):
        """Test that cannot move to COMPLETED without completing setup."""
        fresh_start_academic_year.status = AcademicYear.Status.COMPLETED
        # setup_completed is still False
        
        with pytest.raises(ValidationError) as exc_info:
            fresh_start_academic_year.full_clean()
        
        assert "setup_completed must be True" in str(exc_info.value)


@pytest.mark.django_db
class TestGradeCreationByStatus:
    """Test grade creation permissions based on academic year status."""
    
    def test_grades_allowed_in_setup_status(self, fresh_start_academic_year):
        """Test that grades can be created during SETUP status."""
        assert fresh_start_academic_year.status == AcademicYear.Status.SETUP
        assert fresh_start_academic_year.can_accept_grades() is True
        
        grade = Grade.objects.create(
            name="Setup Grade",
            grade="1",
            academic_year=fresh_start_academic_year,
        )
        
        assert grade.pk is not None
    
    def test_grades_allowed_in_enrollment_status(self, setup_completed_academic_year):
        """Test that grades can be created during ENROLLMENT status."""
        assert setup_completed_academic_year.status == AcademicYear.Status.ENROLLMENT
        assert setup_completed_academic_year.can_accept_grades() is True
        
        grade = Grade.objects.create(
            name="Enrollment Grade",
            grade="2",
            academic_year=setup_completed_academic_year,
        )
        
        assert grade.pk is not None
    
    def test_grades_not_allowed_in_active_status(self, active_academic_year):
        """Test that grades typically cannot be created during ACTIVE status."""
        assert active_academic_year.status == AcademicYear.Status.ACTIVE
        assert active_academic_year.can_accept_grades() is False
    
    def test_grades_not_allowed_in_completed_status(self, completed_academic_year):
        """Test that grades cannot be created for COMPLETED academic year."""
        assert completed_academic_year.status == AcademicYear.Status.COMPLETED
        assert completed_academic_year.can_accept_grades() is False


@pytest.mark.django_db
class TestSetupCompletionEdgeCases:
    """Test edge cases for setup completion."""
    
    def test_reverting_from_enrollment_to_setup_is_invalid(self, setup_completed_academic_year):
        """Test that cannot revert from ENROLLMENT back to SETUP."""
        assert setup_completed_academic_year.status == AcademicYear.Status.ENROLLMENT
        
        # Try to revert to SETUP
        setup_completed_academic_year.status = AcademicYear.Status.SETUP
        # setup_completed is True, which is invalid for SETUP
        
        with pytest.raises(ValidationError) as exc_info:
            setup_completed_academic_year.full_clean()
        
        assert "Cannot be in SETUP status when setup is already completed" in str(exc_info.value)
    
    def test_cannot_uncomplete_setup_for_non_setup_status(self, setup_completed_academic_year):
        """Test that cannot set setup_completed=False for non-SETUP status."""
        assert setup_completed_academic_year.status == AcademicYear.Status.ENROLLMENT
        
        # Try to uncomplete setup
        setup_completed_academic_year.setup_completed = False
        
        with pytest.raises(ValidationError) as exc_info:
            setup_completed_academic_year.full_clean()
        
        assert "setup_completed must be True" in str(exc_info.value)
    
    def test_multiple_transitions_forward(self, fresh_start_academic_year):
        """Test transitioning through multiple statuses."""
        # Start in SETUP
        assert fresh_start_academic_year.status == AcademicYear.Status.SETUP
        
        # Move to ENROLLMENT
        fresh_start_academic_year.setup_completed = True
        fresh_start_academic_year.status = AcademicYear.Status.ENROLLMENT
        fresh_start_academic_year.save()
        fresh_start_academic_year.full_clean()
        
        # Move to ACTIVE
        fresh_start_academic_year.status = AcademicYear.Status.ACTIVE
        fresh_start_academic_year.save()
        fresh_start_academic_year.full_clean()
        
        # Move to COMPLETED
        fresh_start_academic_year.status = AcademicYear.Status.COMPLETED
        fresh_start_academic_year.save()
        fresh_start_academic_year.full_clean()
        
        assert fresh_start_academic_year.status == AcademicYear.Status.COMPLETED
        assert fresh_start_academic_year.setup_completed is True
