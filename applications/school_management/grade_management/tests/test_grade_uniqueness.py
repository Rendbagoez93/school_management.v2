"""
Test Use Cases: Grade Uniqueness & Duplicate Prevention

Real-World Scenarios:
1. Duplicate Grade Definition (same name, grade, year, type, subtype)
2. Same Class Name Across Different Years
3. Same Grade Level Different Sections

✔ Expectations:
  - Prevent duplicate definitions
  - Allow cross-year repetition
  - Allow multiple sections

✔ Real-world protection:
  - Prevents enrollment mapping conflicts
  - Prevents attendance mapping conflicts
  - Prevents teacher assignment conflicts
  - Allows normal school operations (sections, yearly cycles)
"""

import pytest
from django.db.utils import IntegrityError

from applications.school_management.grade_management.models import Grade


@pytest.mark.django_db
class TestDuplicateGradePrevention:
    """Test prevention of duplicate grade definitions."""
    
    def test_duplicate_grade_definition_blocked(self, setup_academic_year):
        """
        Test: Duplicate Grade Definition
        
        Scenario:
          Admin tries to create duplicate:
            - Same name
            - Same grade
            - Same academic_year
            - Same grade_type
            - Same grade_subtype
        
        Expectation:
          ✔ Database IntegrityError
        
        Real-world protection:
          Prevents:
            ❌ Two "Class A – Grade 10 – 2026" records
          
          Which would destroy:
            - Enrollment mapping
            - Attendance mapping
            - Teacher assignment
        """
        # Create first grade
        grade1 = Grade.objects.create(
            name="Class A",
            grade="Grade 10",
            grade_type="Secondary",
            grade_subtype="Science",
            academic_year=setup_academic_year,
        )
        
        assert grade1.pk is not None
        
        # Attempt to create duplicate with exact same values
        with pytest.raises(IntegrityError):
            Grade.objects.create(
                name="Class A",
                grade="Grade 10",
                grade_type="Secondary",
                grade_subtype="Science",
                academic_year=setup_academic_year,
            )
    
    def test_duplicate_without_optional_fields_blocked(self, setup_academic_year):
        """Test duplicate detection when optional fields are empty."""
        # Create first grade without optional fields
        grade1 = Grade.objects.create(
            name="Class A",
            grade="Grade 10",
            grade_type="",  # Empty
            grade_subtype="",  # Empty
            academic_year=setup_academic_year,
        )
        
        assert grade1.pk is not None
        
        # Attempt duplicate
        with pytest.raises(IntegrityError):
            Grade.objects.create(
                name="Class A",
                grade="Grade 10",
                grade_type="",
                grade_subtype="",
                academic_year=setup_academic_year,
            )
    
    def test_duplicate_with_different_description_still_blocked(self, setup_academic_year):
        """
        Test that duplicates are blocked even if description differs.
        
        Description is not part of unique_together, so different descriptions
        don't make grades unique.
        """
        Grade.objects.create(
            name="Class A",
            grade="Grade 10",
            academic_year=setup_academic_year,
            description="First description",
        )
        
        # Same grade with different description - still duplicate
        with pytest.raises(IntegrityError):
            Grade.objects.create(
                name="Class A",
                grade="Grade 10",
                academic_year=setup_academic_year,
                description="Different description",
            )
    
    def test_protection_against_enrollment_mapping_conflicts(self, setup_academic_year, student_user):
        """
        Test real-world protection: Prevent enrollment mapping destruction.
        
        If duplicates were allowed:
          ❌ Student enrolled in "Class A - Grade 10"
          ❌ Which Class A? First one or second one?
          ❌ System breaks down
        """
        from applications.school_management.academic_management.models import StudentEnrollment
        
        # Create grade
        grade = Grade.objects.create(
            name="Class A",
            grade="Grade 10",
            academic_year=setup_academic_year,
        )
        
        # Enroll student
        enrollment = StudentEnrollment.objects.create(
            student=student_user,
            grade=grade,
            academic_year=setup_academic_year,
        )
        
        assert enrollment.grade == grade
        
        # Attempting to create duplicate would break enrollment mapping
        with pytest.raises(IntegrityError):
            Grade.objects.create(
                name="Class A",
                grade="Grade 10",
                academic_year=setup_academic_year,
            )
        
        # System correctly prevents this corruption


@pytest.mark.django_db
class TestCrossYearGradeNames:
    """Test that same grade names are allowed across different years."""
    
    def test_same_class_name_across_different_years_allowed(self, setup_academic_year, previous_academic_year):
        """
        Test: Same Class Name Across Different Years
        
        Scenario:
          ✔ "Class A – Grade 10"
          ✔ 2025/2026
          ✔ 2026/2027
        
        Expectation:
          ✔ Allowed.
        
        Real-world logic:
          Class naming repeats yearly.
          "Class A Grade 10" exists every year.
        """
        # Create grade in current year
        grade_2026 = Grade.objects.create(
            name="Class A",
            grade="Grade 10",
            grade_type="Secondary",
            academic_year=setup_academic_year,  # 2026/2027
        )
        
        # Create same grade in previous year - should be allowed
        grade_2025 = Grade.objects.create(
            name="Class A",
            grade="Grade 10",
            grade_type="Secondary",
            academic_year=previous_academic_year,  # 2025/2026
        )
        
        # Both grades exist
        assert grade_2026.pk is not None
        assert grade_2025.pk is not None
        assert grade_2026.pk != grade_2025.pk
        
        # Same name and grade level, different years
        assert grade_2026.name == grade_2025.name
        assert grade_2026.grade == grade_2025.grade
        assert grade_2026.academic_year != grade_2025.academic_year
    
    def test_yearly_grade_cycle(self, setup_academic_year, enrollment_academic_year):
        """
        Test that schools can repeat grade structures yearly.
        
        Real-world: Grade structure typically repeats each year.
        """
        # Create grade in first year
        grade_year1 = Grade.objects.create(
            name="Class A",
            grade="Grade 10",
            academic_year=setup_academic_year,
        )
        
        # Create same structure in second year
        grade_year2 = Grade.objects.create(
            name="Class A",
            grade="Grade 10",
            academic_year=enrollment_academic_year,
        )
        
        # Both allowed because different academic years
        assert grade_year1.pk != grade_year2.pk
        assert Grade.objects.filter(name="Class A", grade="Grade 10").count() == 2
    
    def test_complete_grade_structure_repeats_yearly(self, setup_academic_year, previous_academic_year):
        """
        Test that entire grade structures can repeat across years.
        
        Real-world: Schools have the same grade structure every year.
        """
        # Define standard grade structure
        grade_structure = [
            {"name": "Class A", "grade": "Grade 9"},
            {"name": "Class B", "grade": "Grade 9"},
            {"name": "Class A", "grade": "Grade 10"},
            {"name": "Class B", "grade": "Grade 10"},
        ]
        
        # Create structure in current year
        for data in grade_structure:
            Grade.objects.create(
                academic_year=setup_academic_year,
                **data
            )
        
        # Create same structure in previous year
        for data in grade_structure:
            Grade.objects.create(
                academic_year=previous_academic_year,
                **data
            )
        
        # All grades created successfully
        assert Grade.objects.filter(academic_year=setup_academic_year).count() == 4
        assert Grade.objects.filter(academic_year=previous_academic_year).count() == 4


@pytest.mark.django_db
class TestMultipleSectionsSameGrade:
    """Test that multiple sections of same grade level are allowed."""
    
    def test_same_grade_level_different_sections_allowed(self, setup_academic_year):
        """
        Test: Same Grade Level Different Sections
        
        Scenario:
          ✔ "Class A – Grade 10"
          ✔ "Class B – Grade 10"
        
        Expectation:
          ✔ Allowed.
        
        Real-world meaning:
          Sections / homerooms.
          Multiple classes for same grade level.
        """
        # Create Class A
        grade_a = Grade.objects.create(
            name="Class A",
            grade="Grade 10",
            grade_type="Secondary",
            academic_year=setup_academic_year,
        )
        
        # Create Class B - same grade level, different section
        grade_b = Grade.objects.create(
            name="Class B",
            grade="Grade 10",
            grade_type="Secondary",
            academic_year=setup_academic_year,
        )
        
        # Both should exist
        assert grade_a.pk is not None
        assert grade_b.pk is not None
        assert grade_a.pk != grade_b.pk
        
        # Same grade level, different names (sections)
        assert grade_a.grade == grade_b.grade
        assert grade_a.name != grade_b.name
    
    def test_multiple_sections_for_capacity(self, enrollment_academic_year):
        """
        Test creating multiple sections to handle student capacity.
        
        Real-world: Schools create A, B, C sections for same grade.
        """
        sections = ["A", "B", "C", "D"]
        grades = []
        
        for section in sections:
            grade = Grade.objects.create(
                name=f"Class {section}",
                grade="Grade 10",
                grade_type="Secondary",
                academic_year=enrollment_academic_year,
            )
            grades.append(grade)
        
        # All sections created
        assert len(grades) == 4
        
        # All are distinct
        grade_ids = {g.pk for g in grades}
        assert len(grade_ids) == 4
        
        # All same grade level
        grade_levels = {g.grade for g in grades}
        assert len(grade_levels) == 1
        assert list(grade_levels)[0] == "Grade 10"
    
    def test_specialized_sections_same_grade(self, setup_academic_year):
        """
        Test creating specialized sections for same grade level.
        
        Real-world: Science track, Arts track, Regular track.
        """
        # Regular section
        regular = Grade.objects.create(
            name="Class A",
            grade="Grade 10",
            grade_type="Secondary",
            grade_subtype="Regular",
            academic_year=setup_academic_year,
        )
        
        # Science section
        science = Grade.objects.create(
            name="Class A",
            grade="Grade 10",
            grade_type="Secondary",
            grade_subtype="Science",
            academic_year=setup_academic_year,
        )
        
        # Arts section
        arts = Grade.objects.create(
            name="Class A",
            grade="Grade 10",
            grade_type="Secondary",
            grade_subtype="Arts",
            academic_year=setup_academic_year,
        )
        
        # All three exist (differentiated by subtype)
        assert regular.pk is not None
        assert science.pk is not None
        assert arts.pk is not None
        
        # All same name and grade, different subtypes
        assert regular.name == science.name == arts.name
        assert regular.grade == science.grade == arts.grade
        assert regular.grade_subtype != science.grade_subtype != arts.grade_subtype
    
    def test_combinations_create_unique_grades(self, setup_academic_year):
        """
        Test that unique_together allows various combinations.
        
        unique_together = (name, grade, academic_year, grade_type, grade_subtype)
        """
        # Same name, different everything else
        grade1 = Grade.objects.create(
            name="Class A",
            grade="Grade 10",
            grade_type="Primary",
            grade_subtype="A",
            academic_year=setup_academic_year,
        )
        
        grade2 = Grade.objects.create(
            name="Class A",
            grade="Grade 10",
            grade_type="Secondary",
            grade_subtype="B",
            academic_year=setup_academic_year,
        )
        
        # Both allowed because type and subtype differ
        assert grade1.pk != grade2.pk


@pytest.mark.django_db
class TestGradeQueryingAndFiltering:
    """Test that duplicate prevention doesn't interfere with normal operations."""
    
    def test_can_query_grades_by_name(self, multiple_grades_same_year):
        """Test querying grades by name returns all matching grades."""
        # multiple_grades_same_year creates Class A, Class B, Class C
        class_a_grades = Grade.objects.filter(name="Class A")
        
        # Should find at least one Class A
        assert class_a_grades.exists()
    
    def test_can_query_grades_by_level(self, multiple_grades_same_year):
        """Test querying grades by level returns all sections."""
        # All have same grade level
        grade_10_sections = Grade.objects.filter(grade="Grade 10")
        
        # Should find all sections
        assert grade_10_sections.count() >= 3
    
    def test_can_query_grades_by_academic_year(self, multiple_grades_same_year, enrollment_academic_year):
        """Test querying grades by academic year."""
        grades = Grade.objects.filter(academic_year=enrollment_academic_year)
        
        # Should find all grades in that year
        assert grades.count() >= 3
