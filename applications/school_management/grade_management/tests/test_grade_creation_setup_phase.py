"""
Test Use Case 1: Creating a Grade During Setup Phase

Real-World Scenario:
Academic Year → SETUP
Admin creates:
  - name → "Class A"
  - grade → "Grade 10"
  - academic_year → 2026/2027

✔ System Behavior:
  - Grade saved successfully
  - Students → Optional
  - Used for curriculum & scheduling setup

✔ Real-world meaning:
  School is designing structure before students join.
"""

import pytest

from applications.school_management.grade_management.models import Grade
from applications.school_management.academic_management.models import AcademicYear


@pytest.mark.django_db
class TestGradeCreationDuringSetup:
    """Test grade creation during SETUP phase."""
    
    def test_can_create_grade_in_setup_phase(self, setup_academic_year):
        """Test that grades can be created when academic year is in SETUP status."""
        # Verify academic year is in SETUP status
        assert setup_academic_year.status == AcademicYear.Status.SETUP
        assert setup_academic_year.setup_completed is False
        
        # Create grade
        grade = Grade.objects.create(
            name="Class A",
            grade="Grade 10",
            grade_type="Secondary",
            academic_year=setup_academic_year,
            description="Grade 10 Section A",
        )
        
        # Verify grade was created successfully
        assert grade.pk is not None
        assert grade.name == "Class A"
        assert grade.grade == "Grade 10"
        assert grade.academic_year == setup_academic_year
        assert grade.is_active is True
    
    def test_grade_policy_allows_setup_phase(self, setup_academic_year):
        """Test that Grade.can_be_created_for_year returns True for SETUP status."""
        assert Grade.can_be_created_for_year(setup_academic_year) is True
        assert setup_academic_year.can_accept_grades() is True
    
    def test_students_optional_during_setup(self, grade_in_setup):
        """Test that grades can exist without students during SETUP phase."""
        # Grade exists without any enrolled students
        assert grade_in_setup.students.count() == 0
        
        # Verify this is valid and expected behavior
        assert grade_in_setup.pk is not None
        assert grade_in_setup.is_active is True
    
    def test_grade_used_for_structure_design(self, setup_academic_year):
        """
        Test that grades created during SETUP are meant for 
        curriculum and scheduling setup, not immediate student enrollment.
        """
        # Create multiple grades for different subjects/sections
        grades = [
            Grade.objects.create(
                name=f"Class {section}",
                grade="Grade 10",
                grade_type="Secondary",
                grade_subtype=f"Section {section}",
                academic_year=setup_academic_year,
                description=f"Grade 10 Section {section} - For structure setup",
            )
            for section in ["A", "B", "C"]
        ]
        
        # All grades created successfully
        assert len(grades) == 3
        
        # None have students yet (structure design phase)
        for grade in grades:
            assert grade.students.count() == 0
            assert grade.academic_year.status == AcademicYear.Status.SETUP
    
    def test_multiple_grades_same_level_different_sections(self, setup_academic_year):
        """
        Test creating multiple sections of the same grade level during SETUP.
        Real-world: Planning multiple homerooms.
        """
        grade_a = Grade.objects.create(
            name="Class A",
            grade="Grade 10",
            grade_type="Secondary",
            academic_year=setup_academic_year,
        )
        
        grade_b = Grade.objects.create(
            name="Class B",
            grade="Grade 10",
            grade_type="Secondary",
            academic_year=setup_academic_year,
        )
        
        # Both should exist independently
        assert grade_a.pk != grade_b.pk
        assert grade_a.name != grade_b.name
        assert grade_a.grade == grade_b.grade  # Same grade level
        assert grade_a.academic_year == grade_b.academic_year
    
    def test_grade_with_metadata_during_setup(self, setup_academic_year):
        """
        Test creating grades with rich metadata during setup phase.
        Real-world: Detailed planning with types and descriptions.
        """
        grade = Grade.objects.create(
            name="Advanced Science Class",
            grade="Grade 10",
            grade_type="Secondary",
            grade_subtype="Science Track",
            description="Advanced curriculum focusing on STEM subjects",
            academic_year=setup_academic_year,
        )
        
        assert grade.pk is not None
        assert grade.grade_type == "Secondary"
        assert grade.grade_subtype == "Science Track"
        assert "STEM" in grade.description
    
    def test_grade_accessible_via_academic_year_relation(self, setup_academic_year):
        """Test that grades can be accessed through academic year relationship."""
        # Create multiple grades
        for i in range(3):
            Grade.objects.create(
                name=f"Class {chr(65 + i)}",  # A, B, C
                grade="Grade 10",
                academic_year=setup_academic_year,
            )
        
        # Access grades through academic year
        grades = setup_academic_year.grades.all()
        assert grades.count() == 3
        
        # Verify all belong to the same academic year
        for grade in grades:
            assert grade.academic_year == setup_academic_year
    
    def test_setup_phase_is_correct_time_for_grade_creation(self, setup_academic_year):
        """
        Test the real-world meaning: SETUP phase is the correct time
        for planning the school structure.
        """
        # Verify setup phase properties
        assert setup_academic_year.is_in_setup is True
        assert setup_academic_year.setup_completed is False
        
        # Grade creation should be allowed
        assert Grade.can_be_created_for_year(setup_academic_year) is True
        
        # Create a grade to represent planned structure
        grade = Grade.objects.create(
            name="Foundation Class",
            grade="Grade 9",
            academic_year=setup_academic_year,
            description="Structure planned before students arrive",
        )
        
        assert grade.pk is not None
        assert grade.students.count() == 0  # No students yet, just planning
