from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from config.roles import RoleEnum
from shared.base_models import BaseSoftDeletableModel


class ActiveStaffManager(models.Manager):
	"""Manager that returns only active, non-deleted staff members."""

	def get_queryset(self):
		return super().get_queryset().filter(is_active=True, is_deleted=False)


class StaffMember(BaseSoftDeletableModel):
	"""Represents a non-teaching staff member linked to a user account.

	This model holds operational data (employee ID, department, job title)
	for school staff. The owning user must not be a Student.
	"""

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

	active = ActiveStaffManager()

	class Meta:
		ordering = ["employee_id"]
		indexes = [
			models.Index(fields=["department"]),
			models.Index(fields=["is_active"]),
		]
		verbose_name = "Staff Member"
		verbose_name_plural = "Staff Members"

	def __str__(self) -> str:
		return f"{self.employee_id} — {self.user.get_full_name()}"

	def clean(self) -> None:
		super().clean()
		if self.employee_id:
			self.employee_id = self.employee_id.strip().upper()
		if not self.employee_id:
			raise ValidationError({"employee_id": "Employee ID is required."})
		if self.user_id and self.user.groups.filter(name=RoleEnum.STUDENT.value).exists():
			raise ValidationError({"user": "A student account cannot be assigned to a staff role."})
		if self.user_id and self.user.groups.filter(name=RoleEnum.PARENT.value).exists():
			raise ValidationError({"user": "A parent account cannot be assigned to a staff role."})

	def save(self, *args, **kwargs) -> None:
		self.clean()
		super().save(*args, **kwargs)
