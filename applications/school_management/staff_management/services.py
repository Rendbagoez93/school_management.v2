"""Service layer for staff_management.

Encapsulates all business logic for StaffMember operations.
Views should delegate to this module rather than querying models directly.
"""

import structlog
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.utils import IntegrityError

from .models import StaffMember
from .schemas import StaffMemberCreateSchema, StaffMemberUpdateSchema

logger = structlog.get_logger(__name__)

User = get_user_model()


class StaffMemberService:
	"""All operations related to StaffMember lifecycle."""

	# ------------------------------------------------------------------
	# Queries
	# ------------------------------------------------------------------

	@staticmethod
	def get_by_id(staff_id: int) -> StaffMember | None:
		"""Return a StaffMember by PK (non-deleted), or None."""
		return (
			StaffMember.objects.select_related("user")
			.filter(pk=staff_id, is_deleted=False)
			.first()
		)

	@staticmethod
	def get_by_employee_id(employee_id: str) -> StaffMember | None:
		"""Return a StaffMember by employee_id (case-insensitive), or None."""
		return (
			StaffMember.objects.select_related("user")
			.filter(employee_id__iexact=employee_id.strip(), is_deleted=False)
			.first()
		)

	@staticmethod
	def list_staff(
		department: str | None = None,
		is_active: bool | None = None,
		search: str | None = None,
	):
		"""Return a queryset of non-deleted staff, with optional filters."""
		qs = StaffMember.objects.select_related("user").filter(is_deleted=False)
		if department:
			qs = qs.filter(department__iexact=department)
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
	def create(data: StaffMemberCreateSchema) -> StaffMember:
		"""Create a StaffMember profile.

		Args:
			data: Validated creation payload.

		Raises:
			ValidationError: If user not found, already has a profile, or fails model validation.
		"""
		try:
			user = User.objects.get(pk=data.user_id)
		except User.DoesNotExist:
			raise ValidationError({"user_id": "User not found."})

		if StaffMember.objects.filter(user=user, is_deleted=False).exists():
			raise ValidationError({"user_id": "This user already has a staff member profile."})

		try:
			member = StaffMember(
				user=user,
				employee_id=data.employee_id,
				department=data.department,
				job_title=data.job_title,
				date_of_joining=data.date_of_joining,
				is_active=True,
			)
			member.save()
		except IntegrityError:
			raise ValidationError({"employee_id": f"Employee ID '{data.employee_id}' is already in use."})

		logger.info(
			"staff_member_created",
			staff_id=member.pk,
			employee_id=member.employee_id,
			user_id=str(user.pk),
		)
		return member

	@staticmethod
	@transaction.atomic
	def update(member: StaffMember, data: StaffMemberUpdateSchema) -> StaffMember:
		"""Apply a partial update to a StaffMember.

		Only fields that are not None in ``data`` are updated.
		"""
		changed = False
		if data.department is not None:
			member.department = data.department
			changed = True
		if data.job_title is not None:
			member.job_title = data.job_title
			changed = True
		if data.date_of_joining is not None:
			member.date_of_joining = data.date_of_joining
			changed = True

		if changed:
			member.save(update_fields=["department", "job_title", "date_of_joining", "date_modified"])
			logger.info("staff_member_updated", staff_id=member.pk, employee_id=member.employee_id)

		return member

	@staticmethod
	@transaction.atomic
	def set_active(member: StaffMember, *, is_active: bool) -> StaffMember:
		"""Activate or deactivate a StaffMember."""
		if member.is_active == is_active:
			return member

		member.is_active = is_active
		member.save(update_fields=["is_active", "date_modified"])
		action = "activated" if is_active else "deactivated"
		logger.info(f"staff_member_{action}", staff_id=member.pk, employee_id=member.employee_id)
		return member

	@staticmethod
	@transaction.atomic
	def delete(member: StaffMember) -> None:
		"""Soft-delete a StaffMember."""
		member.delete()
		logger.info("staff_member_deleted", staff_id=member.pk, employee_id=member.employee_id)
