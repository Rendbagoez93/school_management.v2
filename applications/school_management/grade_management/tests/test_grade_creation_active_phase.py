"""
Test Use Case 3: Creating Grade During ACTIVE Phase

Real-World Scenario:
Academic Year → ACTIVE
Admin tries to create "Grade 10D"

✔ Expectation:
  Raise ValidationError: "Cannot create grades for academic year ..."

✔ Correct behavior.

✔ Real-world protection:
  Prevents structural instability mid-semester.

Otherwise:
  ❌ Schedules break
  ❌ Attendance mapping breaks
  ❌ Gradebooks become inconsistent
"""

import pytest
from django.core.exceptions import ValidationError

from applications.school_management.grade_management.models import Grade
from applications.school_management.academic_management.models import AcademicYear


@pytest.mark.django_db
class TestGradeCreationDuringActive:
    """Test grade creation restrictions during ACTIVE phase."""
    
    def test_cannot_create_grade_in_active_phase(self, active_academic_year):
        """Test that grades CANNOT be created when academic year is in ACTIVE status."""
        # Verify academic year is in ACTIVE status
        assert active_academic_year.status == AcademicYear.Status.ACTIVE
        assert active_academic_year.setup_completed is True
        
        # Attempt to create grade should fail
        with pytest.raises(ValidationError) as exc_info:
            Grade.objects.create(
                name="Grade 10D",
                grade="Grade 10",
                grade_type="Secondary",
                academic_year=active_academic_year,
                description="Attempting to create during ACTIVE phase",
            )
        
        # Verify error message is appropriate
        error_dict = exc_info.value.message_dict
        assert "academic_year" in error_dict
        assert "Cannot create grades" in str(error_dict["academic_year"])
        assert "SETUP or ENROLLMENT" in str(error_dict["academic_year"])
    
    def test_grade_policy_blocks_active_phase(self, active_academic_year):
        """Test that Grade.can_be_created_for_year returns False for ACTIVE status."""
        assert Grade.can_be_created_for_year(active_academic_year) is False
        assert active_academic_year.can_accept_grades() is False
    
    def test_protection_against_schedule_disruption(self, active_academic_year):
        """
        Test real-world protection: Prevent schedule disruption.
        
        If grades could be created during ACTIVE phase:
          ❌ Existing schedules would be invalidated
          ❌ Teacher assignments would be disrupted
          ❌ Classroom allocations would conflict
        """
        # Academic year is active
        assert active_academic_year.status == AcademicYear.Status.ACTIVE
        
        # Attempting to add a new grade would disrupt schedules
        with pytest.raises(ValidationError) as exc_info:
            Grade.objects.create(
                name="Disruptive Class",
                grade="Grade 10",
                academic_year=active_academic_year,
                description="Would break schedules if allowed",
            )
        
        # System correctly prevents this
        assert "Cannot create grades" in str(exc_info.value)
    
    def test_protection_against_attendance_mapping_breaks(self, active_academic_year):
        """
        Test real-world protection: Prevent attendance mapping issues.
        
        If grades could be created during ACTIVE phase:
          ❌ Attendance systems wouldn't know about new grade
          ❌ Historical attendance data could be corrupted
          ❌ Daily attendance workflows would break
        """
        # Attempt to create grade that would break attendance mapping
        with pytest.raises(ValidationError):
            Grade.objects.create(
                name="Attendance Breaker",
                grade="Grade 10",
                academic_year=active_academic_year,
            )
        
        # System protects data integrity
        assert Grade.objects.filter(
            name="Attendance Breaker",
            academic_year=active_academic_year
        ).count() == 0
    
    def test_protection_against_gradebook_inconsistency(self, active_academic_year):
        """
        Test real-world protection: Prevent gradebook inconsistencies.
        
        If grades could be created during ACTIVE phase:
          ❌ Gradebooks for existing grades already have assignments/grades
          ❌ New grade would have no historical data
          ❌ Reporting would be inconsistent
        """
        # Active phase means grading is in progress
        assert active_academic_year.status == AcademicYear.Status.ACTIVE
        
        # Cannot add new grade that would have incomplete gradebook
        with pytest.raises(ValidationError):
            Grade.objects.create(
                name="Late Grade",
                grade="Grade 10",
                academic_year=active_academic_year,
                description="Would have incomplete gradebook history",
            )
    
    def test_existing_grades_remain_accessible(self, grade_in_active):
        """
        Test that existing grades (created before ACTIVE phase) remain accessible.
        
        Real-world: Grades created during SETUP/ENROLLMENT should still work
        during ACTIVE phase - just can't create NEW ones.
        """
        # Grade exists and is accessible
        assert grade_in_active.pk is not None
        assert grade_in_active.is_active is True
        assert grade_in_active.academic_year.status == AcademicYear.Status.ACTIVE
        
        # Can query and use existing grade
        grade = Grade.objects.get(pk=grade_in_active.pk)
        assert grade == grade_in_active
    
    def test_cannot_bypass_via_different_parameters(self, active_academic_year):
        """
        Test that grade creation is blocked regardless of parameters used.
        
        Ensure the protection is robust.
        """
        # Try with minimal parameters
        with pytest.raises(ValidationError):
            Grade.objects.create(
                name="Bypass Attempt 1",
                grade="Grade 10",
                academic_year=active_academic_year,
            )
        
        # Try with full parameters
        with pytest.raises(ValidationError):
            Grade.objects.create(
                name="Bypass Attempt 2",
                grade="Grade 10",
                grade_type="Secondary",
                grade_subtype="Science",
                description="Trying to bypass with full params",
                academic_year=active_academic_year,
                is_active=True,
            )
        
        # Verify no grades were created
        assert Grade.objects.filter(
            academic_year=active_academic_year,
            name__startswith="Bypass Attempt"
        ).count() == 0
    
    def test_error_message_is_clear_and_helpful(self, active_academic_year):
        """
        Test that the error message clearly explains why creation is blocked.
        """
        with pytest.raises(ValidationError) as exc_info:
            Grade.objects.create(
                name="Test Grade",
                grade="Grade 10",
                academic_year=active_academic_year,
            )
        
        error_message = str(exc_info.value)
        
        # Error should mention:
        # - Cannot create grades
        # - The academic year name
        # - Required status (SETUP or ENROLLMENT)
        assert "Cannot create grades" in error_message
        assert active_academic_year.name in error_message or "SETUP" in error_message
        assert "ENROLLMENT" in error_message
    
    def test_active_phase_designed_for_operations_not_structure_changes(self, active_academic_year):
        """
        Test that ACTIVE phase is designed for daily operations, not structural changes.
        
        Real-world meaning:
          ACTIVE = Classes in session
          - Teaching happens
          - Attendance recorded
          - Assignments given
          - Grades recorded
          
          Structure is LOCKED to maintain stability.
        """
        # Active phase characteristics
        assert active_academic_year.status == AcademicYear.Status.ACTIVE
        assert active_academic_year.setup_completed is True
        
        # Grade structure should be locked
        assert Grade.can_be_created_for_year(active_academic_year) is False
        
        # This is correct behavior to maintain operational stability
        with pytest.raises(ValidationError):
            Grade.objects.create(
                name="Structural Change",
                grade="Grade 10",
                academic_year=active_academic_year,
            )
        
        # System correctly prioritizes stability over flexibility during ACTIVE phase
