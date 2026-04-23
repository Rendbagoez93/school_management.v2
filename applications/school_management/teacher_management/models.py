from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from config.roles import RoleEnum
from shared.base_models import BaseSoftDeletableModel


class ActiveTeacherManager(models.Manager):
	"""Returns only active, non-deleted Teacher records."""

	def get_queryset(self):
		return super().get_queryset().filter(is_active=True, is_deleted=False)


class Teacher(BaseSoftDeletableModel):
	"""Represents a teaching staff member's professional profile.

	A Teacher record links to a User account that holds the TEACHER group role.
	It stores teaching-specific data (employee ID, department, specialization).

	Relationship to user_management:
	  - SchoolUserManager.create_teacher() creates the User + SchoolStaff profile.
	  - TeacherService.create() in this module creates the Teacher profile
	    separately, allowing full decoupling of user account creation from
	    the teacher's professional record.
	"""

	user = models.OneToOneField(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name="teacher_profile",
	)
	employee_id = models.CharField(max_length=32, unique=True, db_index=True)
	department = models.CharField(max_length=100, blank=True)
	specialization = models.CharField(max_length=120, blank=True)
	date_of_joining = models.DateField(null=True, blank=True)
	is_active = models.BooleanField(default=True)

	objects = models.Manager()
	active = ActiveTeacherManager()

	class Meta:
		ordering = ["employee_id"]
		indexes = [
			models.Index(fields=["department"]),
			models.Index(fields=["is_active"]),
		]
		verbose_name = "Teacher"
		verbose_name_plural = "Teachers"

	def __str__(self) -> str:
		return f"{self.employee_id} — {self.user.get_full_name()}"

	def clean(self) -> None:
		super().clean()
		if self.employee_id:
			self.employee_id = self.employee_id.strip().upper()
		if not self.employee_id:
			raise ValidationError({"employee_id": "Employee ID is required."})
		if self.user_id and not self.user.groups.filter(name=RoleEnum.TEACHER.value).exists():
			raise ValidationError({"user": "Teacher profile requires the Teacher group role."})
		if self.user_id and self.user.groups.filter(name=RoleEnum.STUDENT.value).exists():
			raise ValidationError({"user": "A student account cannot be assigned a teacher profile."})

	def save(self, *args, **kwargs) -> None:
		self.clean()
		super().save(*args, **kwargs)
