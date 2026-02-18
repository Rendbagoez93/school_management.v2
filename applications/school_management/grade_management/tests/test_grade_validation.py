"""
Test Use Cases: Grade Field Validation

Real-World Scenarios:
1. Grade Level Missing (admin forgets grade = '')
2. Grade Level Blank Spaces (grade = '      ')
3. Grade Level Too Long (grade = "VeryVeryVeryVeryLongGradeDefinition")

✔ Expectations:
  - Raise appropriate ValidationError
  - Prevent data corruption
  - Ensure data quality

✔ Real-world protection:
  - Prevents ambiguous class definitions
  - Prevents invisible data corruption
  - Prevents UI & indexing problems
  - Ensures reporting works correctly
"""

import pytest
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError

from applications.school_management.grade_management.models import Grade


@pytest.mark.django_db
class TestGradeLevelValidation:
    """Test validation of grade level field."""
    
    def test_grade_level_missing_raises_error(self, setup_academic_year):
        """
        Test: Grade Level Missing
        
        Scenario:
          Admin forgets -> grade = ''
        
        Expectation:
          Raise: "Grade level is mandatory."
        
        Real-world protection:
          ✔ Prevents ambiguous class definitions
          Without grade level:
            ❌ Reporting becomes impossible
            ❌ Promotion logic breaks
        """
        with pytest.raises(ValidationError) as exc_info:
            Grade.objects.create(
                name="Class A",
                grade="",  # Empty grade level
                academic_year=setup_academic_year,
            )
        
        # Check error message
        error_dict = exc_info.value.message_dict
        assert "grade" in error_dict
        assert "Grade level is mandatory" in str(error_dict["grade"])
    
    def test_grade_level_none_raises_error(self, setup_academic_year):
        """
        Test: Grade level as None
        
        Some forms might pass None instead of empty string.
        """
        with pytest.raises(ValidationError) as exc_info:
            Grade.objects.create(
                name="Class A",
                grade=None,
                academic_year=setup_academic_year,
            )
        
        # Should raise validation error
        error_dict = exc_info.value.message_dict
        assert "grade" in error_dict
    
    def test_grade_level_blank_spaces_raises_error(self, setup_academic_year):
        """
        Test: Grade Level Blank Spaces
        
        Scenario:
          grade = '      '
        
        Expectation:
          Raise: "Cannot be empty or just blank spaces"
        
        Real-world protection:
          ✔ Prevents invisible data corruption
          Blank spaces would:
            ❌ Look empty in UI
            ❌ Break searches
            ❌ Corrupt reports
        """
        with pytest.raises(ValidationError) as exc_info:
            Grade.objects.create(
                name="Class A",
                grade="      ",  # Only blank spaces
                academic_year=setup_academic_year,
            )
        
        # Check error message
        error_dict = exc_info.value.message_dict
        assert "grade" in error_dict
        assert "Cannot be empty or just blank spaces" in str(error_dict["grade"])
    
    def test_grade_level_whitespace_variations_rejected(self, setup_academic_year):
        """Test various whitespace-only inputs are rejected."""
        whitespace_variations = [
            "   ",      # Spaces
            "\t\t",     # Tabs
            "\n\n",     # Newlines
            "  \t  ",   # Mixed
            " \n \t ",  # All mixed
        ]
        
        for whitespace in whitespace_variations:
            with pytest.raises(ValidationError) as exc_info:
                Grade.objects.create(
                    name="Test Class",
                    grade=whitespace,
                    academic_year=setup_academic_year,
                )
            
            error_dict = exc_info.value.message_dict
            assert "grade" in error_dict
    
    def test_grade_level_too_long_raises_error(self, setup_academic_year):
        """
        Test: Grade Level Too Long
        
        Scenario:
          grade = "VeryVeryVeryVeryLongGradeDefinition"
        
        Expectation:
          Raise: "Grade level too long"
        
        Real-world protection:
          ✔ Prevents UI & indexing problems
          Too long would:
            ❌ Break UI layouts
            ❌ Slow down database queries
            ❌ Cause display issues
        """
        # Create a grade level longer than 32 characters
        long_grade = "VeryVeryVeryVeryLongGradeDefinitionThatExceedsLimit"
        assert len(long_grade) > 32
        
        with pytest.raises(ValidationError) as exc_info:
            Grade.objects.create(
                name="Class A",
                grade=long_grade,
                academic_year=setup_academic_year,
            )
        
        # Check error message
        error_dict = exc_info.value.message_dict
        assert "grade" in error_dict
        assert "Grade level too long" in str(error_dict["grade"])
        assert "max 32 characters" in str(error_dict["grade"])
    
    def test_grade_level_at_max_length_allowed(self, setup_academic_year):
        """Test that grade level at exactly 32 characters is allowed."""
        # Create exactly 32 character grade level
        max_length_grade = "A" * 32
        assert len(max_length_grade) == 32
        
        # Should be created successfully
        grade = Grade.objects.create(
            name="Class A",
            grade=max_length_grade,
            academic_year=setup_academic_year,
        )
        
        assert grade.pk is not None
        assert len(grade.grade) == 32
    
    def test_grade_level_just_over_max_length_rejected(self, setup_academic_year):
        """Test that grade level at 33 characters is rejected."""
        # Create 33 character grade level (1 over limit)
        over_max_grade = "A" * 33
        assert len(over_max_grade) == 33
        
        with pytest.raises(ValidationError) as exc_info:
            Grade.objects.create(
                name="Class A",
                grade=over_max_grade,
                academic_year=setup_academic_year,
            )
        
        error_dict = exc_info.value.message_dict
        assert "grade" in error_dict
        assert "too long" in str(error_dict["grade"]).lower()
    
    def test_valid_grade_levels_accepted(self, setup_academic_year):
        """Test that valid grade levels are accepted."""
        valid_grades = [
            "Grade 1",
            "Grade 10",
            "Grade 12",
            "KG",
            "Pre-K",
            "Kindergarten",
            "1",
            "10",
            "Senior",
            "Junior",
        ]
        
        for i, grade_level in enumerate(valid_grades):
            grade = Grade.objects.create(
                name=f"Class {i}",
                grade=grade_level,
                academic_year=setup_academic_year,
            )
            assert grade.pk is not None
            assert grade.grade == grade_level


@pytest.mark.django_db
class TestGradeNameValidation:
    """Test validation of grade name field."""
    
    def test_grade_name_required(self, setup_academic_year):
        """Test that grade name is required (database constraint)."""
        # Note: name field doesn't have blank=True, so Django requires it
        # This is enforced at the form/serializer level primarily
        # Database will enforce NOT NULL
        
        with pytest.raises((ValidationError, IntegrityError)):
            Grade.objects.create(
                name="",
                grade="Grade 10",
                academic_year=setup_academic_year,
            )
    
    def test_grade_name_max_length(self, setup_academic_year):
        """Test that grade name respects max_length of 64 characters."""
        # At 64 characters - should work
        max_length_name = "A" * 64
        grade = Grade.objects.create(
            name=max_length_name,
            grade="Grade 10",
            academic_year=setup_academic_year,
        )
        assert grade.pk is not None
        
        # Over 64 characters - should fail at database level
        # Django will truncate or raise error depending on database
        over_max_name = "A" * 65
        # This might raise ValidationError or database error
        with pytest.raises((ValidationError, Exception)):
            Grade.objects.create(
                name=over_max_name,
                grade="Grade 10",
                academic_year=setup_academic_year,
            )


@pytest.mark.django_db
class TestGradeDescriptionValidation:
    """Test validation of grade description field."""
    
    def test_grade_description_optional(self, setup_academic_year):
        """Test that description is optional."""
        grade = Grade.objects.create(
            name="Class A",
            grade="Grade 10",
            academic_year=setup_academic_year,
            description="",  # Empty description should be allowed
        )
        
        assert grade.pk is not None
        assert grade.description == ""
    
    def test_grade_description_can_be_omitted(self, setup_academic_year):
        """Test that description can be completely omitted."""
        grade = Grade.objects.create(
            name="Class A",
            grade="Grade 10",
            academic_year=setup_academic_year,
            # description not provided
        )
        
        assert grade.pk is not None
        assert grade.description == ""
    
    def test_grade_description_accepts_long_text(self, setup_academic_year):
        """Test that description is TextField and can hold long text."""
        long_description = "A" * 1000  # Long text
        
        grade = Grade.objects.create(
            name="Class A",
            grade="Grade 10",
            academic_year=setup_academic_year,
            description=long_description,
        )
        
        assert grade.pk is not None
        assert len(grade.description) == 1000


@pytest.mark.django_db
class TestGradeTypeValidation:
    """Test validation of grade_type and grade_subtype fields."""
    
    def test_grade_type_optional(self, setup_academic_year):
        """Test that grade_type is optional."""
        grade = Grade.objects.create(
            name="Class A",
            grade="Grade 10",
            academic_year=setup_academic_year,
            grade_type="",  # Empty is allowed
        )
        
        assert grade.pk is not None
        assert grade.grade_type == ""
    
    def test_grade_subtype_optional(self, setup_academic_year):
        """Test that grade_subtype is optional."""
        grade = Grade.objects.create(
            name="Class A",
            grade="Grade 10",
            academic_year=setup_academic_year,
            grade_subtype="",  # Empty is allowed
        )
        
        assert grade.pk is not None
        assert grade.grade_subtype == ""
    
    def test_grade_type_max_length(self, setup_academic_year):
        """Test that grade_type respects max_length of 32 characters."""
        # At 32 characters - should work
        max_type = "A" * 32
        grade = Grade.objects.create(
            name="Class A",
            grade="Grade 10",
            grade_type=max_type,
            academic_year=setup_academic_year,
        )
        assert grade.pk is not None
        assert len(grade.grade_type) == 32
    
    def test_grade_subtype_max_length(self, setup_academic_year):
        """Test that grade_subtype respects max_length of 32 characters."""
        # At 32 characters - should work
        max_subtype = "A" * 32
        grade = Grade.objects.create(
            name="Class A",
            grade="Grade 10",
            grade_subtype=max_subtype,
            academic_year=setup_academic_year,
        )
        assert grade.pk is not None
        assert len(grade.grade_subtype) == 32
