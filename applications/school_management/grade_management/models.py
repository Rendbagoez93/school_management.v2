from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from applications.school_management.academic_management.models import AcademicYear, StudentEnrollment
from shared.base_models import BaseSoftDeletableModel


class Grade(BaseSoftDeletableModel):
    """Represents a class/section for a specific academic year."""

    name = models.CharField(max_length=64)
    description = models.TextField(blank=True)
    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.CASCADE,
        related_name="grades",
    )
    grade = models.CharField(max_length=32)
    grade_type = models.CharField(max_length=32, blank=True)
    grade_subtype = models.CharField(max_length=32, blank=True)
    students = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through=StudentEnrollment,
        blank=True,
        related_name="student_grades",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("name", "grade", "academic_year", "grade_type", "grade_subtype")
        ordering = ["-academic_year", "name"]
        indexes = [
            models.Index(fields=["academic_year", "grade"]),
            models.Index(fields=["grade", "grade_type", "grade_subtype"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.grade})"
    
    @classmethod
    def can_be_created_for_year(cls, academic_year) -> bool:
        return academic_year.can_accept_grades()
    
    def clean(self):
        super().clean()
        if not self.grade:
            raise ValidationError({
                "grade": "Grade level is mandatory."
            })
            
        grade_str = str(self.grade).strip()
        if not grade_str:
            raise ValidationError({
                "grade": "Cannot be empty or just blank spaces"
            })
        if len(grade_str) > 32:
            raise ValidationError({
                "grade": f"Grade level too long ({len(grade_str)}) max 32 characters allowed."
            })
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def delete(self, using=None, keep_parents=False):
        """Override delete to cascade soft-delete to related StudentGrade records."""
        from django.utils import timezone
        
        # Soft delete all related StudentEnrollment records
        StudentEnrollment.objects.filter(grade=self).update(
            is_deleted=True,
            deleted_at=timezone.now()
        )
        
        # Perform soft delete on this Grade
        super().delete(using=using, keep_parents=keep_parents)
