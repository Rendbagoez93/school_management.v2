from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from applications.school_management.academic_management.models import StudentEnrollment
from shared.base_models import BaseSoftDeletableModel


class ActiveStudentsManager(models.Manager):
    """Manager for M2M that only returns non-deleted enrollments."""
    def get_queryset(self):
        # Filter through relationship to exclude soft-deleted enrollments
        return super().get_queryset().filter(
            student_grades__is_deleted=False
        )


class Grade(BaseSoftDeletableModel):
    """Represents a class/section for a specific academic year."""

    name = models.CharField(max_length=64)
    description = models.TextField(blank=True)
    academic_year = models.ForeignKey(
        "academic_management.AcademicYear",
        on_delete=models.CASCADE,
        related_name="grades",
    )
    grade = models.CharField(max_length=32)
    grade_type = models.CharField(max_length=32, blank=True)
    grade_subtype = models.CharField(max_length=32, blank=True)
    students = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through="academic_management.StudentEnrollment",
        blank=True,
        related_name="student_grades",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def get_active_students(self):
        """Get students with active (non-soft-deleted) enrollments."""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        # Query through the StudentEnrollment to filter by is_deleted
        enrollment_ids = StudentEnrollment.objects.filter(
            grade=self,
            is_deleted=False
        ).values_list('student_id', flat=True)
        return User.objects.filter(id__in=enrollment_ids)

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
        
        # Validate name field
        if not self.name or not self.name.strip():
            raise ValidationError({
                "name": "Grade name is required."
            })
        
        if len(self.name) > 64:
            raise ValidationError({
                "name": f"Grade name too long ({len(self.name)}) max 64 characters allowed."
            })
        
        # Validate academic_year dependency only on creation (not updates)
        if self.academic_year_id and not self.pk and not self.can_be_created_for_year(self.academic_year):
            raise ValidationError({
                "academic_year": f"Cannot create grades for academic year '{self.academic_year.name}'. "
                                 f"Academic year must be in SETUP or ENROLLMENT status."
            })
        
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
        # Only validate model fields, not uniqueness constraints
        # This allows database-level IntegrityError for duplicates
        self.clean()
        super().save(*args, **kwargs)

    def delete(self, using=None, keep_parents=False):
        """Override delete to cascade soft-delete to related StudentEnrollment records."""
        # Soft delete all related StudentEnrollment records
        StudentEnrollment.objects.filter(grade=self).update(
            is_deleted=True,
            deleted_at=timezone.now()
        )
        
        # Perform soft delete on this Grade
        super().delete(using=using, keep_parents=keep_parents)
