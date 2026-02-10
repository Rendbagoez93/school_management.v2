from django.core.exceptions import ValidationError
from django.db import models

from applications.school_management.academic_management.models import AcademicYear
from shared.base_models import BaseSoftDeletableModel


class AcademicYearSetup(BaseSoftDeletableModel):
    """Tracks the setup progress for an academic year."""

    class SetupSteps(models.TextChoices):
        BASIC_INFO = "BASIC_INFO", "Basic Information"
        IMPORT_GRADES = "IMPORT_GRADES", "Import Grades"
        IMPORT_STUDENTS = "IMPORT_STUDENTS", "Import Students"
        ASSIGN_CLASSROOMS = "ASSIGN_CLASSROOMS", "Assign Classrooms"
        REVIEW = "REVIEW", "Review and Confirm"
        COMPLETED = "COMPLETED", "Setup Completed"

    academic_year = models.OneToOneField(AcademicYear, on_delete=models.CASCADE, related_name="setup_progress")
    current_step = models.CharField(max_length=20, choices=SetupSteps.choices, default=SetupSteps.BASIC_INFO)
    basic_info_completed = models.BooleanField(default=False)
    import_grades_completed = models.BooleanField(default=False)
    import_students_completed = models.BooleanField(default=False)
    assign_classrooms_completed = models.BooleanField(default=False)
    review_completed = models.BooleanField(default=False)

    # Track data import method choices
    class ImportMethod(models.TextChoices):
        NONE = "NONE", "Not Imported"
        MANUAL = "MANUAL", "Manual Entry"
        CSV = "CSV", "CSV File Upload"
        API = "API", "API Integration"

    grades_import_method = models.CharField(max_length=10, choices=ImportMethod.choices, default=ImportMethod.NONE)
    students_import_method = models.CharField(max_length=10, choices=ImportMethod.choices, default=ImportMethod.NONE)
    classrooms_import_method = models.CharField(max_length=10, choices=ImportMethod.choices, default=ImportMethod.NONE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Setup for {self.academic_year.name}"
    
    def clean(self):
        """Validate that import methods match completion status."""
        super().clean()
        
        # Validate grades import
        if self.import_grades_completed and self.grades_import_method == self.ImportMethod.NONE:
            raise ValidationError({
                "grades_import_method": "Import method must be specified when grades import is marked as completed."
            })
        
        # Validate students import
        if self.import_students_completed and self.students_import_method == self.ImportMethod.NONE:
            raise ValidationError({
                "students_import_method": "Import method must be specified when students import is marked as completed."
            })
        
        # Validate classrooms assignment
        if self.assign_classrooms_completed and self.classrooms_import_method == self.ImportMethod.NONE:
            raise ValidationError({
                "classrooms_import_method": (
                    "Import method must be specified when classroom assignment is marked as completed."
                )
            })
    
    def is_complete(self) -> bool:
        return all([
            self.basic_info_completed,
            self.import_grades_completed,
            self.import_students_completed,
            self.assign_classrooms_completed,
            self.review_completed,
        ])
    
    def is_ready(self) -> bool:
        return self.is_complete()


class ImportTask(BaseSoftDeletableModel):
    """Tracks data import tasks during academic year setup."""

    class TaskType(models.TextChoices):
        GRADES = "GRADES", "Grades"
        STUDENTS = "STUDENTS", "Students"
        CLASSROOMS = "CLASSROOMS", "Classrooms"

    class TaskStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        IN_PROGRESS = "IN_PROGRESS", "In Progress"
        COMPLETED = "COMPLETED", "Completed"
        FAILED = "FAILED", "Failed"

    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name="import_tasks")
    task_type = models.CharField(max_length=20, choices=TaskType.choices)
    status = models.CharField(max_length=20, choices=TaskStatus.choices, default=TaskStatus.PENDING)
    file_path = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Path to import file if applicable",
    )
    total_records = models.IntegerField(default=0)
    processed_records = models.IntegerField(default=0)
    success_count = models.IntegerField(default=0)
    error_count = models.IntegerField(default=0)
    error_details = models.JSONField(
        blank=True,
        null=True,
        help_text="Details of errors encountered during import",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        task = self.get_task_type_display()
        year = self.academic_year.name
        return f"{task} import for {year}"

    @property
    def progress_percentage(self):
        """Calculate the percentage of import completion."""
        if self.total_records == 0:
            return 0
        return (self.processed_records / self.total_records) * 100
