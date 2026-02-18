"""
Test Use Case 4: Creating Grade During COMPLETED Phase

Real-World Scenario:
Academic Year → COMPLETED

✔ Expectation:
  Block creation.

✔ Real-world logic:
  Completed years are archives.
  They should be read-only and immutable.
"""

import pytest
from django.core.exceptions import ValidationError

from applications.school_management.grade_management.models import Grade
from applications.school_management.academic_management.models import AcademicYear


@pytest.mark.django_db
class TestGradeCreationDuringCompleted:
    """Test grade creation restrictions during COMPLETED phase."""
    
    def test_cannot_create_grade_in_completed_phase(self, completed_academic_year):
        """Test that grades CANNOT be created when academic year is COMPLETED."""
        # Verify academic year is COMPLETED
        assert completed_academic_year.status == AcademicYear.Status.COMPLETED
        assert completed_academic_year.is_active is False
        
        # Attempt to create grade should fail
        with pytest.raises(ValidationError) as exc_info:
            Grade.objects.create(
                name="Late Grade",
                grade="Grade 10",
                grade_type="Secondary",
                academic_year=completed_academic_year,
                description="Attempting to create in completed year",
            )
        
        # Verify error message
        error_dict = exc_info.value.message_dict
        assert "academic_year" in error_dict
        assert "Cannot create grades" in str(error_dict["academic_year"])
    
    def test_grade_policy_blocks_completed_phase(self, completed_academic_year):
        """Test that Grade.can_be_created_for_year returns False for COMPLETED status."""
        assert Grade.can_be_created_for_year(completed_academic_year) is False
        assert completed_academic_year.can_accept_grades() is False
    
    def test_completed_years_are_archives(self, completed_academic_year):
        """
        Test real-world meaning: Completed years are archives.
        
        Archives should be:
          ✔ Read-only
          ✔ Immutable
          ✔ Historical records
          ✔ Not modifiable
        """
        # Completed year characteristics
        assert completed_academic_year.status == AcademicYear.Status.COMPLETED
        assert completed_academic_year.setup_completed is True
        
        # Should not accept new grades (would violate archive integrity)
        with pytest.raises(ValidationError):
            Grade.objects.create(
                name="Archive Violation",
                grade="Grade 10",
                academic_year=completed_academic_year,
            )
        
        # System correctly protects archived data
    
    def test_historical_grade_data_remains_accessible(self, grade_in_completed):
        """
        Test that existing grades from completed years remain accessible.
        
        Real-world: Historical data must be preserved and queryable
        for reports, transcripts, etc.
        """
        # Grade from completed year is accessible
        assert grade_in_completed.pk is not None
        assert grade_in_completed.academic_year.status == AcademicYear.Status.COMPLETED
        
        # Can query historical data
        grade = Grade.objects.get(pk=grade_in_completed.pk)
        assert grade == grade_in_completed
        
        # Data integrity preserved
        assert grade.name == grade_in_completed.name
        assert grade.grade == grade_in_completed.grade
    
    def test_cannot_add_grades_to_past_years(self, completed_academic_year):
        """
        Test that you cannot retroactively add grades to past academic years.
        
        Real-world protection:
          ❌ Cannot modify historical records
          ❌ Transcripts would become inconsistent
          ❌ Reports would be unreliable
        """
        # Attempting to add grade to past year
        with pytest.raises(ValidationError):
            Grade.objects.create(
                name="Retroactive Grade",
                grade="Grade 10",
                academic_year=completed_academic_year,
                description="Trying to modify historical data",
            )
        
        # Historical integrity protected
        assert Grade.objects.filter(
            name="Retroactive Grade",
            academic_year=completed_academic_year
        ).count() == 0
    
    def test_completed_status_prevents_all_structural_changes(self, completed_academic_year):
        """
        Test that COMPLETED status prevents all structural modifications.
        
        Real-world: Once a year is completed, its structure is frozen.
        """
        # Try various grade types - all should be blocked
        test_cases = [
            {"name": "New Primary", "grade": "Grade 1", "grade_type": "Primary"},
            {"name": "New Secondary", "grade": "Grade 10", "grade_type": "Secondary"},
            {"name": "New Special", "grade": "Special", "grade_type": "Special Education"},
        ]
        
        for test_data in test_cases:
            with pytest.raises(ValidationError):
                Grade.objects.create(
                    academic_year=completed_academic_year,
                    **test_data
                )
        
        # No new grades created
        for test_data in test_cases:
            assert Grade.objects.filter(
                name=test_data["name"],
                academic_year=completed_academic_year
            ).count() == 0
    
    def test_completed_year_is_not_active(self, completed_academic_year):
        """
        Test that completed years are marked as inactive.
        
        Real-world: Inactive years should not be available for new operations.
        """
        assert completed_academic_year.is_active is False
        assert completed_academic_year.status == AcademicYear.Status.COMPLETED
        
        # Cannot create grades in inactive year
        with pytest.raises(ValidationError):
            Grade.objects.create(
                name="Inactive Year Test",
                grade="Grade 10",
                academic_year=completed_academic_year,
            )
    
    def test_protection_against_historical_data_corruption(self, completed_academic_year):
        """
        Test protection against corrupting historical data.
        
        If grades could be added to completed years:
          ❌ Student transcripts would be inconsistent
          ❌ Historical reports would be wrong
          ❌ Graduation records would be unreliable
          ❌ Compliance audits would fail
        """
        # Completed year has historical significance
        assert completed_academic_year.status == AcademicYear.Status.COMPLETED
        
        # Adding grades would corrupt historical records
        with pytest.raises(ValidationError):
            Grade.objects.create(
                name="Historical Corruption",
                grade="Grade 12",
                academic_year=completed_academic_year,
                description="Would corrupt graduation records",
            )
        
        # System prevents historical data corruption
    
    def test_error_message_for_completed_year(self, completed_academic_year):
        """Test that error message is clear for completed years."""
        with pytest.raises(ValidationError) as exc_info:
            Grade.objects.create(
                name="Test Grade",
                grade="Grade 10",
                academic_year=completed_academic_year,
            )
        
        error_message = str(exc_info.value)
        
        # Error should indicate that grades can only be created in SETUP or ENROLLMENT
        assert "Cannot create grades" in error_message
        assert "SETUP" in error_message or "ENROLLMENT" in error_message
    
    def test_completed_phase_designed_for_historical_queries_only(self, completed_academic_year, grade_in_completed):
        """
        Test that COMPLETED phase is designed for read-only historical access.
        
        Real-world meaning:
          COMPLETED = Archive mode
          - Read historical data ✔
          - Generate reports ✔
          - Produce transcripts ✔
          - Modify structure ❌
        """
        # Can read existing grades
        grades = Grade.objects.filter(academic_year=completed_academic_year)
        assert grade_in_completed in grades
        
        # Cannot add new grades
        with pytest.raises(ValidationError):
            Grade.objects.create(
                name="New Grade",
                grade="Grade 10",
                academic_year=completed_academic_year,
            )
        
        # This is correct behavior for maintaining historical integrity
        assert Grade.can_be_created_for_year(completed_academic_year) is False
