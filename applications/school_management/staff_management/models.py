from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from config.roles import RoleEnum
from shared.base_models import BaseSoftDeletableModel


class StaffMember(BaseSoftDeletableModel):
	"""Represents a non-teaching staff member linked to a user account."""

	user = models.OneToOneField(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name="staff_member_profile",
	)
	employee_id = models.CharField(max_length=32, unique=True, db_index=True)
	department = models.CharField(max_length=100, blank=True)
	job_title = models.CharField(max_length=100, blank=True)
	date_of_joining = models.DateField(null=True, blank=True)
	is_active = models.BooleanField(default=True)

	class Meta:
		ordering = ["employee_id"]
		indexes = [
			models.Index(fields=["department"]),
			models.Index(fields=["is_active"]),
		]

	def __str__(self) -> str:
		return f"{self.employee_id} - {self.user.get_full_name()}"

	def clean(self) -> None:
		super().clean()
		if self.user_id and self.user.groups.filter(name=RoleEnum.STUDENT.value).exists():
			raise ValidationError({"user": "A student account cannot be assigned to staff."})


class Teacher(BaseSoftDeletableModel):
	"""Represents a teaching staff member linked to a user account."""

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

	class Meta:
		ordering = ["employee_id"]
		indexes = [
			models.Index(fields=["department"]),
			models.Index(fields=["is_active"]),
		]

	def __str__(self) -> str:
		return f"{self.employee_id} - {self.user.get_full_name()}"

	def clean(self) -> None:
		super().clean()
		if self.user_id and not self.user.groups.filter(name=RoleEnum.TEACHER.value).exists():
			raise ValidationError({"user": "Teacher profile requires the Teacher group role."})
