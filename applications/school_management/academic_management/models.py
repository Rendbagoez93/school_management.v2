from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from shared.base_models import BaseSoftDeletableModel


class AcademicYear(BaseSoftDeletableModel):
    """Represents an academic year/session."""

    class Status(models.TextChoices):
        SETUP = "SETUP", "Setup Phase"
        ENROLLMENT = "ENROLLMENT", "Enrollment Phase"
        ACTIVE = "ACTIVE", "Active"
        COMPLETED = "COMPLETED", "Completed"

    class DeploymentType(models.TextChoices):
        FRESH_START = "FRESH_START", "Fresh Start (New Academic Year)"
        MID_YEAR = "MID_YEAR", "Mid-Year Adoption"

    name = models.CharField(max_length=32, unique=True)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.SETUP,
        help_text="Current status of the academic year",
    )
    deployment_type = models.CharField(
        max_length=20,
        choices=DeploymentType.choices,
        default=DeploymentType.FRESH_START,
        help_text="Whether this is a fresh academic year or mid-year adoption",
    )
    setup_completed = models.BooleanField(
        default=False,
        help_text="Whether the initial setup process has been completed",
    )
    # Optional enrollment period dates (can be null for mid-year adoption)
    enrollment_start_date = models.DateField(
        null=True,
        blank=True,
        help_text="Start date for enrollment period (optional for mid-year adoption)",
    )
    enrollment_end_date = models.DateField(
        null=True,
        blank=True,
        help_text="End date for enrollment period (optional for mid-year adoption)",
    )

    def __str__(self):
        return self.name

    def clean(self):
        super().clean()
        
        if self.start_date >= self.end_date:
            raise ValidationError("Start date must be before end date.")
        
        if (self.enrollment_start_date or self.enrollment_end_date) and (
            not self.enrollment_start_date or not self.enrollment_end_date
        ):
            raise ValidationError("Both enrollment start and end dates must be set.")
        
        if self.enrollment_start_date and self.enrollment_end_date and not (
            self.start_date <= self.enrollment_start_date < self.enrollment_end_date <= self.end_date
        ):
            raise ValidationError("Enrollment period must be within academic year dates.")

        if self.deployment_type == self.DeploymentType.MID_YEAR and self.status == self.Status.ENROLLMENT:
            raise ValidationError("Mid-year adoption should not have an enrollment phase.")
        
        # Validate status and setup_completed consistency
        if self.status != self.Status.SETUP and not self.setup_completed:
            raise ValidationError("setup_completed must be True when status is not SETUP.")
        
        if self.status == self.Status.SETUP and self.setup_completed:
            raise ValidationError("Cannot be in SETUP status when setup is already completed.")


    @property
    def is_in_setup(self):
        """Check if academic year is in setup phase."""
        return self.status == self.Status.SETUP

    @property
    def is_in_enrollment(self):
        """Check if academic year is in enrollment phase."""
        return self.status == self.Status.ENROLLMENT
    
    @property
    def is_active_year(self):
        """Check if academic year is active."""
        return self.status in {self.Status.SETUP, self.Status.ENROLLMENT, self.Status.ACTIVE}
    
    def can_accept_grades(self) -> bool:
        return self.status in {self.Status.SETUP, self.Status.ENROLLMENT}


class StudentEnrollment(BaseSoftDeletableModel):
    """Through model to ensure a student is only in
    one class per academic year."""

    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    grade = models.ForeignKey("Grade", on_delete=models.CASCADE)
    academic_year = models.ForeignKey("AcademicYear", on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("student", "academic_year")
        indexes = [
            models.Index(fields=["academic_year"]),
            models.Index(fields=["grade"]),
            models.Index(fields=["student"]),
        ]
        verbose_name = "Grade Student"
        verbose_name_plural = "Grade Students"

    def __str__(self):
        return f"{self.pk}"

