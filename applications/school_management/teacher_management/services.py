"""Service layer for teacher_management.

All business logic for Teacher profile operations lives here.
Views and external callers should use this module exclusively.
"""

import structlog
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.utils import IntegrityError

from config.roles import RoleEnum

from .models import Teacher
from .schemas import TeacherCreateSchema, TeacherUpdateSchema

logger = structlog.get_logger(__name__)

User = get_user_model()


class TeacherService:
	"""Lifecycle operations for Teacher profiles."""

	# ------------------------------------------------------------------
	# Queries
	# ------------------------------------------------------------------

	@staticmethod
	def get_by_id(teacher_id: int) -> Teacher | None:
		"""Return a Teacher by PK (non-deleted), or None."""
		return (
			Teacher.objects.select_related("user")
			.filter(pk=teacher_id, is_deleted=False)
			.first()
		)

	@staticmethod
	def get_by_employee_id(employee_id: str) -> Teacher | None:
		"""Return a Teacher by employee_id (case-insensitive), or None."""
		return (
			Teacher.objects.select_related("user")
			.filter(employee_id__iexact=employee_id.strip(), is_deleted=False)
			.first()
		)

	@staticmethod
	def get_by_user(user) -> Teacher | None:
		"""Return the Teacher profile for a given user, or None."""
		return (
			Teacher.objects.select_related("user")
			.filter(user=user, is_deleted=False)
			.first()
		)

	@staticmethod
	def list_teachers(
		department: str | None = None,
		specialization: str | None = None,
		is_active: bool | None = None,
		search: str | None = None,
	):
		"""Return a queryset of non-deleted teachers, with optional filters."""
		qs = Teacher.objects.select_related("user").filter(is_deleted=False)
		if department:
			qs = qs.filter(department__iexact=department)
		if specialization:
			qs = qs.filter(specialization__icontains=specialization)
		if is_active is not None:
			qs = qs.filter(is_active=is_active)
		if search:
			qs = qs.filter(
				user__first_name__icontains=search
			) | qs.filter(
				user__last_name__icontains=search
			) | qs.filter(
				employee_id__icontains=search
			)
		return qs.order_by("employee_id")

	# ------------------------------------------------------------------
	# Commands
	# ------------------------------------------------------------------

	@staticmethod
	@transaction.atomic
	def create(data: TeacherCreateSchema) -> Teacher:
		"""Create a Teacher profile for an existing user.

		The user must already have the Teacher role group assigned (e.g. via
		SchoolUserManager.create_teacher). This service creates the professional
		profile only — it does not create the underlying User account.

		Args:
			data: Validated creation payload.

		Raises:
			ValidationError: If user not found, missing Teacher role, already has
			                 a profile, or fails model-level validation.
		"""
		try:
			user = User.objects.get(pk=data.user_id)
		except User.DoesNotExist:
			raise ValidationError({"user_id": "User not found."})

		if not user.groups.filter(name=RoleEnum.TEACHER.value).exists():
			raise ValidationError({"user_id": "User does not have the Teacher role."})

		if Teacher.objects.filter(user=user, is_deleted=False).exists():
			raise ValidationError({"user_id": "This user already has a teacher profile."})

		try:
			teacher = Teacher(
				user=user,
				employee_id=data.employee_id,
				department=data.department,
				specialization=data.specialization,
				date_of_joining=data.date_of_joining,
				is_active=True,
			)
			teacher.save()
		except IntegrityError:
			raise ValidationError({"employee_id": f"Employee ID '{data.employee_id}' is already in use."})

		logger.info(
			"teacher_created",
			teacher_id=teacher.pk,
			employee_id=teacher.employee_id,
			user_id=str(user.pk),
		)
		return teacher

	@staticmethod
	@transaction.atomic
	def update(teacher: Teacher, data: TeacherUpdateSchema) -> Teacher:
		"""Apply a partial update to a Teacher profile.

		Only fields that are not None in ``data`` are updated.
		"""
		changed = False
		if data.department is not None:
			teacher.department = data.department
			changed = True
		if data.specialization is not None:
			teacher.specialization = data.specialization
			changed = True
		if data.date_of_joining is not None:
			teacher.date_of_joining = data.date_of_joining
			changed = True

		if changed:
			teacher.save(
				update_fields=["department", "specialization", "date_of_joining", "date_modified"]
			)
			logger.info(
				"teacher_updated",
				teacher_id=teacher.pk,
				employee_id=teacher.employee_id,
			)

		return teacher

	@staticmethod
	@transaction.atomic
	def set_active(teacher: Teacher, *, is_active: bool) -> Teacher:
		"""Activate or deactivate a Teacher profile."""
		if teacher.is_active == is_active:
			return teacher

		teacher.is_active = is_active
		teacher.save(update_fields=["is_active", "date_modified"])
		action = "activated" if is_active else "deactivated"
		logger.info(f"teacher_{action}", teacher_id=teacher.pk, employee_id=teacher.employee_id)
		return teacher

	@staticmethod
	@transaction.atomic
	def delete(teacher: Teacher) -> None:
		"""Soft-delete a Teacher profile."""
		teacher.delete()
		logger.info("teacher_deleted", teacher_id=teacher.pk, employee_id=teacher.employee_id)
