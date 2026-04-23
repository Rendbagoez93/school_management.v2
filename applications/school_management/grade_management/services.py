"""Service layer for grade_management.

Encapsulates all business logic for Grade and StudentEnrollment operations.
Views and external callers should use this module exclusively.
"""

import structlog
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.utils import IntegrityError

from applications.school_management.academic_management.models import AcademicYear, StudentEnrollment

from .grade_factory import GradeFactory
from .models import Grade
from .schemas import GradeCreateSchema, GradeUpdateSchema

logger = structlog.get_logger(__name__)

User = get_user_model()


class GradeService:
	"""Lifecycle operations for Grade profiles and student enrollments."""

	# ------------------------------------------------------------------
	# Queries
	# ------------------------------------------------------------------

	@staticmethod
	def get_by_id(grade_id: int) -> Grade | None:
		"""Return a Grade by PK (non-deleted), or None."""
		return (
			Grade.objects.select_related("academic_year")
			.filter(pk=grade_id, is_deleted=False)
			.first()
		)

	@staticmethod
	def list_grades(
		academic_year_id: int | None = None,
		grade: str | None = None,
		is_active: bool | None = None,
		search: str | None = None,
	):
		"""Return a queryset of non-deleted grades, with optional filters."""
		qs = Grade.objects.select_related("academic_year").filter(is_deleted=False)
		if academic_year_id is not None:
			qs = qs.filter(academic_year_id=academic_year_id)
		if grade:
			qs = qs.filter(grade__iexact=grade)
		if is_active is not None:
			qs = qs.filter(is_active=is_active)
		if search:
			qs = qs.filter(name__icontains=search)
		return qs.order_by("grade", "name")

	# ------------------------------------------------------------------
	# Commands
	# ------------------------------------------------------------------

	@staticmethod
	@transaction.atomic
	def create(data: GradeCreateSchema) -> Grade:
		"""Create a Grade using GradeFactory.

		Raises:
			ValidationError: If the academic year is not found, in wrong status,
			                 or a duplicate grade already exists.
		"""
		try:
			academic_year = AcademicYear.objects.get(pk=data.academic_year_id, is_deleted=False)
		except AcademicYear.DoesNotExist:
			raise ValidationError({"academic_year_id": "Academic year not found."})

		try:
			grade_obj = GradeFactory.create_grade(
				academic_year=academic_year,
				name=data.name,
				grade=data.grade,
				grade_type=data.grade_type,
				grade_subtype=data.grade_subtype,
				description=data.description,
			)
		except IntegrityError:
			raise ValidationError(
				{"name": "A grade with this name already exists for this academic year and grade level."}
			)

		logger.info(
			"grade_created",
			grade_id=grade_obj.pk,
			name=grade_obj.name,
			academic_year_id=academic_year.pk,
		)
		return grade_obj

	@staticmethod
	@transaction.atomic
	def update(grade_obj: Grade, data: GradeUpdateSchema) -> Grade:
		"""Apply a partial update to a Grade.

		Only fields that are not None in ``data`` are applied.
		is_active=False is handled correctly (False is not None).
		"""
		changed = False
		for field in ("name", "description", "grade_type", "grade_subtype"):
			value = getattr(data, field)
			if value is not None:
				setattr(grade_obj, field, value)
				changed = True

		if data.is_active is not None:
			grade_obj.is_active = data.is_active
			changed = True

		if changed:
			try:
				grade_obj.save()
			except IntegrityError:
				raise ValidationError(
					{"name": "A grade with this name already exists for this academic year."}
				)
			logger.info("grade_updated", grade_id=grade_obj.pk, name=grade_obj.name)

		return grade_obj

	@staticmethod
	@transaction.atomic
	def delete(grade_obj: Grade) -> None:
		"""Soft-delete a Grade (cascades to related StudentEnrollments)."""
		grade_obj.delete()
		logger.info("grade_deleted", grade_id=grade_obj.pk, name=grade_obj.name)

	# ------------------------------------------------------------------
	# Student enrollment
	# ------------------------------------------------------------------

	@staticmethod
	def get_enrollment(grade_id: int, student_id: str) -> StudentEnrollment | None:
		"""Return the active enrollment for a student in a grade, or None."""
		return (
			StudentEnrollment.objects.filter(
				grade_id=grade_id,
				student_id=student_id,
				is_deleted=False,
			)
			.first()
		)

	@staticmethod
	@transaction.atomic
	def enroll_student(grade_obj: Grade, student_id: str) -> StudentEnrollment:
		"""Enroll a student in a grade.

		Raises:
			ValidationError: If the student doesn't exist or is already enrolled
			                 in this academic year.
		"""
		try:
			student = User.objects.get(pk=student_id)
		except User.DoesNotExist:
			raise ValidationError({"student_id": "Student not found."})

		if StudentEnrollment.objects.filter(
			academic_year=grade_obj.academic_year,
			student=student,
			is_deleted=False,
		).exists():
			raise ValidationError(
				{"student_id": "Student is already enrolled in this academic year."}
			)

		enrollment = StudentEnrollment.objects.create(
			student=student,
			grade=grade_obj,
			academic_year=grade_obj.academic_year,
		)
		logger.info(
			"student_enrolled",
			enrollment_id=enrollment.pk,
			student_id=str(student.pk),
			grade_id=grade_obj.pk,
		)
		return enrollment

	@staticmethod
	@transaction.atomic
	def unenroll_student(grade_id: int, student_id: str) -> None:
		"""Soft-delete an enrollment (unenroll a student from a grade).

		Raises:
			ValidationError: If the enrollment record does not exist.
		"""
		enrollment = GradeService.get_enrollment(grade_id, student_id)
		if enrollment is None:
			raise ValidationError({"student_id": "Enrollment not found."})

		enrollment.delete()
		logger.info("student_unenrolled", grade_id=grade_id, student_id=str(student_id))
