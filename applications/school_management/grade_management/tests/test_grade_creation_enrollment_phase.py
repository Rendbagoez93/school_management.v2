"""
Test Use Case 2: Creating Grade During Enrollment Phase

Real-World Scenario:
Academic Year → ENROLLMENT
Admin creates "Class B"

✔ Expectation:
  Allowed.

✔ Why this is important:
  Schools often open new sections dynamically based on enrollment numbers.

✔ Example:
  Too many students → Add "Grade 10C"
"""

import pytest

from applications.school_management.grade_management.models import Grade
from applications.school_management.academic_management.models import AcademicYear


@pytest.mark.django_db
class TestGradeCreationDuringEnrollment:
    """Test grade creation during ENROLLMENT phase."""
    
    def test_can_create_grade_in_enrollment_phase(self, enrollment_academic_year):
        """Test that grades can be created when academic year is in ENROLLMENT status."""
        # Verify academic year is in ENROLLMENT status
        assert enrollment_academic_year.status == AcademicYear.Status.ENROLLMENT
        assert enrollment_academic_year.setup_completed is True
        
        # Create grade
        grade = Grade.objects.create(
            name="Class B",
            grade="Grade 10",
            grade_type="Secondary",
            academic_year=enrollment_academic_year,
            description="Dynamically added during enrollment",
        )
        
        # Verify grade was created successfully
        assert grade.pk is not None
        assert grade.name == "Class B"
        assert grade.grade == "Grade 10"
        assert grade.academic_year == enrollment_academic_year
        assert grade.is_active is True
    
    def test_grade_policy_allows_enrollment_phase(self, enrollment_academic_year):
        """Test that Grade.can_be_created_for_year returns True for ENROLLMENT status."""
        assert Grade.can_be_created_for_year(enrollment_academic_year) is True
        assert enrollment_academic_year.can_accept_grades() is True
    
    def test_dynamic_section_addition_based_on_demand(self, enrollment_academic_year, multiple_student_users):
        """
        Test real-world scenario: Adding new section when enrollment exceeds capacity.
        
        Scenario:
          - School has Class A and Class B
          - Too many students enroll
          - Admin adds "Class C" to handle overflow
        """
        # Create initial grades
        Grade.objects.create(
            name="Class A",
            grade="Grade 10",
            academic_year=enrollment_academic_year,
        )
        
        Grade.objects.create(
            name="Class B",
            grade="Grade 10",
            academic_year=enrollment_academic_year,
        )
        
        # Simulate enrollment filling up
        # Assume each class has capacity issues
        initial_grade_count = Grade.objects.filter(
            academic_year=enrollment_academic_year,
            grade="Grade 10"
        ).count()
        
        assert initial_grade_count == 2
        
        # Admin decides to add Class C due to high enrollment
        grade_c = Grade.objects.create(
            name="Class C",
            grade="Grade 10",
            academic_year=enrollment_academic_year,
            description="Added dynamically due to high enrollment",
        )
        
        # Verify new section was added successfully
        assert grade_c.pk is not None
        
        final_grade_count = Grade.objects.filter(
            academic_year=enrollment_academic_year,
            grade="Grade 10"
        ).count()
        
        assert final_grade_count == 3
    
    def test_adding_specialized_sections_during_enrollment(self, enrollment_academic_year):
        """
        Test adding specialized sections based on student interests.
        
        Real-world:
          - During enrollment, school realizes need for specialized sections
          - Science track, Arts track, etc.
        """
        # Add specialized sections
        science_section = Grade.objects.create(
            name="Science Advanced",
            grade="Grade 10",
            grade_type="Secondary",
            grade_subtype="Science Track",
            academic_year=enrollment_academic_year,
            description="Added based on student interest in science",
        )
        
        arts_section = Grade.objects.create(
            name="Arts Advanced",
            grade="Grade 10",
            grade_type="Secondary",
            grade_subtype="Arts Track",
            academic_year=enrollment_academic_year,
            description="Added based on student interest in arts",
        )
        
        # Both sections created successfully
        assert science_section.pk is not None
        assert arts_section.pk is not None
        assert science_section.grade_subtype != arts_section.grade_subtype
    
    def test_enrollment_phase_maintains_flexibility(self, enrollment_academic_year):
        """
        Test that enrollment phase maintains flexibility for structural changes.
        
        Real-world meaning:
          Schools need flexibility during enrollment to respond to demand.
        """
        # Initial state
        initial_count = Grade.objects.filter(academic_year=enrollment_academic_year).count()
        
        # Add grades as needed during enrollment
        new_grades = []
        for section in ["D", "E", "F"]:
            grade = Grade.objects.create(
                name=f"Class {section}",
                grade="Grade 9",
                academic_year=enrollment_academic_year,
                description=f"Section {section} added during enrollment period",
            )
            new_grades.append(grade)
        
        # All grades added successfully
        assert len(new_grades) == 3
        for grade in new_grades:
            assert grade.pk is not None
            assert grade.academic_year.status == AcademicYear.Status.ENROLLMENT
        
        final_count = Grade.objects.filter(academic_year=enrollment_academic_year).count()
        assert final_count == initial_count + 3
    
    def test_grade_creation_after_setup_completed(self, enrollment_academic_year):
        """
        Test that grades can still be created even after setup is completed,
        as long as the year is in ENROLLMENT status.
        """
        # Verify setup is completed but we're in enrollment
        assert enrollment_academic_year.setup_completed is True
        assert enrollment_academic_year.status == AcademicYear.Status.ENROLLMENT
        
        # Can still create grades
        grade = Grade.objects.create(
            name="Late Addition Class",
            grade="Grade 11",
            academic_year=enrollment_academic_year,
            description="Added after setup completion during enrollment",
        )
        
        assert grade.pk is not None
    
    def test_multiple_levels_during_enrollment(self, enrollment_academic_year):
        """
        Test adding grades for multiple grade levels during enrollment.
        
        Real-world: School might add sections for various grade levels 
        based on enrollment patterns.
        """
        grades = []
        for level in [9, 10, 11, 12]:
            grade = Grade.objects.create(
                name=f"Grade {level} Section X",
                grade=f"Grade {level}",
                grade_type="Secondary",
                academic_year=enrollment_academic_year,
                description=f"Grade {level} added during enrollment",
            )
            grades.append(grade)
        
        # All grades across different levels created
        assert len(grades) == 4
        
        # Verify variety of grade levels
        grade_levels = {g.grade for g in grades}
        assert len(grade_levels) == 4
    
    def test_enrollment_phase_grade_accessible_immediately(self, enrollment_academic_year):
        """
        Test that grades created during enrollment are immediately accessible
        for student assignment.
        """
        # Create grade during enrollment
        grade = Grade.objects.create(
            name="Immediate Class",
            grade="Grade 10",
            academic_year=enrollment_academic_year,
        )
        
        # Grade is immediately accessible
        assert grade.is_active is True
        assert grade in enrollment_academic_year.grades.all()
        
        # Can be used for enrollment immediately (students can be added)
        assert grade.students.count() == 0  # No students yet
        # The grade is ready to accept students
