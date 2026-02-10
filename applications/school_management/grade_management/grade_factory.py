"""
Grade Factory

Centralizes all grade creation logic.
This is the ONLY place where Grade objects should be created.
"""

from django.core.exceptions import ValidationError
from django.db import transaction

from applications.school_management.grade_management.models import Grade


class GradeFactory:
    @staticmethod
    @transaction.atomic
    def create_grade(
        academic_year,
        name: str,
        grade: str,
        grade_type: str = "",
        grade_subtype: str = "",
        description: str = "",
    ) -> Grade:
        """
        Create a single grade for an academic year.
        
        Args:
            academic_year: The AcademicYear to create the grade for
            name: Name of the grade/class
            grade: Grade level (e.g., "1", "2", "KG")
            grade_type: Type of grade (optional)
            grade_subtype: Subtype of grade (optional)
            description: Description (optional)
        
        Returns:
            Created Grade object
        
        Raises:
            ValidationError: If grade cannot be created for this academic year
        """
        # Check if grade can be created
        if not Grade.can_be_created_for_year(academic_year):
            raise ValidationError(
                f"Cannot create grades for academic year in {academic_year.get_status_display()} status. "
                "Grades can only be created during SETUP or ENROLLMENT phases."
            )

        # Create the grade
        grade_obj = Grade.objects.create(
            name=name,
            grade=grade,
            grade_type=grade_type,
            grade_subtype=grade_subtype,
            description=description,
            academic_year=academic_year,
            is_active=True,
        )

        return grade_obj

    @staticmethod
    @transaction.atomic
    def bulk_create_grades(academic_year, grades_data: list[dict]) -> list[Grade]:
        # Check if grades can be created
        if not Grade.can_be_created_for_year(academic_year):
            raise ValidationError(
                f"Cannot create grades for academic year in {academic_year.get_status_display()} status. "
                "Grades can only be created during SETUP or ENROLLMENT phases."
            )

        # Build grade objects
        grades = [
            Grade(
                academic_year=academic_year,
                name=data['name'],
                grade=data['grade'],
                grade_type=data.get('grade_type', ''),
                grade_subtype=data.get('grade_subtype', ''),
                description=data.get('description', ''),
                is_active=True,
            )
            for data in grades_data
        ]

        # Bulk create
        return Grade.objects.bulk_create(grades)
