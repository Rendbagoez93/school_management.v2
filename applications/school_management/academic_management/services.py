"""Service layer for academic_management.

Encapsulates all business logic for AcademicYear operations.
Views and external callers should use this module exclusively.
"""

import structlog
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.utils import IntegrityError

from .models import AcademicYear
from .schemas import AcademicYearCreateSchema, AcademicYearUpdateSchema

logger = structlog.get_logger(__name__)

# Allowed forward transitions per status.
# FRESH_START: SETUP → ENROLLMENT → ACTIVE → COMPLETED
# MID_YEAR:    SETUP → ACTIVE → COMPLETED
_STATUS_TRANSITIONS: dict[str, set[str]] = {
	AcademicYear.Status.SETUP: {AcademicYear.Status.ENROLLMENT, AcademicYear.Status.ACTIVE},
	AcademicYear.Status.ENROLLMENT: {AcademicYear.Status.ACTIVE},
	AcademicYear.Status.ACTIVE: {AcademicYear.Status.COMPLETED},
	AcademicYear.Status.COMPLETED: set(),
}


class AcademicYearService:
	"""All operations related to the AcademicYear lifecycle."""

	# ------------------------------------------------------------------
	# Queries
	# ------------------------------------------------------------------

	@staticmethod
	def get_by_id(year_id: int) -> AcademicYear | None:
		"""Return an AcademicYear by PK (non-deleted), or None."""
		return AcademicYear.objects.filter(pk=year_id, is_deleted=False).first()

	@staticmethod
	def list_years(
		status: str | None = None,
		is_active: bool | None = None,
	):
		"""Return a queryset of non-deleted academic years, newest first."""
		qs = AcademicYear.objects.filter(is_deleted=False)
		if status:
			qs = qs.filter(status=status)
		if is_active is not None:
			qs = qs.filter(is_active=is_active)
		return qs.order_by("-start_date")

	# ------------------------------------------------------------------
	# Commands
	# ------------------------------------------------------------------

	@staticmethod
	@transaction.atomic
	def create(data: AcademicYearCreateSchema) -> AcademicYear:
		"""Create a new AcademicYear.

		Raises:
			ValidationError: If the name is already taken or model validation fails.
		"""
		try:
			year = AcademicYear(
				name=data.name,
				start_date=data.start_date,
				end_date=data.end_date,
				deployment_type=data.deployment_type,
				enrollment_start_date=data.enrollment_start_date,
				enrollment_end_date=data.enrollment_end_date,
			)
			year.save()
		except IntegrityError:
			raise ValidationError({"name": f"Academic year '{data.name}' already exists."})

		logger.info("academic_year_created", year_id=year.pk, name=year.name)
		return year

	@staticmethod
	@transaction.atomic
	def update(year: AcademicYear, data: AcademicYearUpdateSchema) -> AcademicYear:
		"""Apply a partial update to an AcademicYear.

		Only fields that are not None in ``data`` are applied.
		"""
		changed = False
		for field in ("name", "start_date", "end_date", "enrollment_start_date", "enrollment_end_date"):
			value = getattr(data, field)
			if value is not None:
				setattr(year, field, value)
				changed = True

		if changed:
			try:
				year.save()
			except IntegrityError:
				raise ValidationError({"name": "That academic year name is already in use."})
			logger.info("academic_year_updated", year_id=year.pk, name=year.name)

		return year

	@staticmethod
	@transaction.atomic
	def transition_status(year: AcademicYear, new_status: str) -> AcademicYear:
		"""Advance an AcademicYear to a new status.

		Enforces allowed transitions and deployment-type rules:
		  - MID_YEAR years cannot enter ENROLLMENT status.
		  - SETUP → any next status requires setup_completed=True.

		Raises:
			ValidationError: If the transition is not allowed.
		"""
		allowed = _STATUS_TRANSITIONS.get(year.status, set())
		if new_status not in allowed:
			raise ValidationError(
				{"status": f"Cannot transition from '{year.status}' to '{new_status}'."}
			)

		if (
			year.deployment_type == AcademicYear.DeploymentType.MID_YEAR
			and new_status == AcademicYear.Status.ENROLLMENT
		):
			raise ValidationError(
				{"status": "Mid-year adoption cannot enter the Enrollment phase."}
			)

		if year.status == AcademicYear.Status.SETUP and not year.setup_completed:
			raise ValidationError(
				{"status": "Setup must be completed before advancing the academic year status."}
			)

		year.status = new_status
		if new_status == AcademicYear.Status.COMPLETED:
			year.is_active = False

		update_fields = ["status", "is_active", "date_modified"]
		year.save(update_fields=update_fields)
		logger.info("academic_year_status_changed", year_id=year.pk, new_status=new_status)
		return year

	@staticmethod
	@transaction.atomic
	def delete(year: AcademicYear) -> None:
		"""Soft-delete an AcademicYear."""
		year.delete()
		logger.info("academic_year_deleted", year_id=year.pk, name=year.name)
