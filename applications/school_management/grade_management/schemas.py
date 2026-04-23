"""Pydantic schemas for the grade_management API.

Defines request/response shapes for Grade and StudentEnrollment operations.
"""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


class GradeCreateSchema(BaseModel):
	"""Payload for creating a new Grade."""

	academic_year_id: int
	name: str = Field(..., min_length=1, max_length=64)
	grade: str = Field(..., min_length=1, max_length=32)
	grade_type: str = Field(default="", max_length=32)
	grade_subtype: str = Field(default="", max_length=32)
	description: str = Field(default="")

	@field_validator("name", "grade", mode="before")
	@classmethod
	def strip_whitespace(cls, v: str) -> str:
		return v.strip() if isinstance(v, str) else v


class GradeUpdateSchema(BaseModel):
	"""Payload for partial update of a Grade.

	All fields are optional; only supplied fields are updated.
	"""

	name: str | None = Field(default=None, min_length=1, max_length=64)
	description: str | None = None
	grade_type: str | None = Field(default=None, max_length=32)
	grade_subtype: str | None = Field(default=None, max_length=32)
	is_active: bool | None = None

	@field_validator("name", mode="before")
	@classmethod
	def strip_whitespace(cls, v: str | None) -> str | None:
		return v.strip() if isinstance(v, str) else v


class GradeListQuerySchema(BaseModel):
	"""Query parameters for listing grades."""

	academic_year_id: int | None = None
	grade: str | None = None
	is_active: bool | None = None
	search: str | None = Field(default=None, max_length=100)


class GradeAcademicYearSchema(BaseModel):
	"""Minimal academic year data embedded in Grade responses."""

	id: int
	name: str
	status: str
	status_display: str

	@classmethod
	def from_model(cls, year) -> GradeAcademicYearSchema:
		return cls(
			id=year.pk,
			name=year.name,
			status=year.status,
			status_display=year.get_status_display(),
		)


class GradeResponseSchema(BaseModel):
	"""Full Grade representation returned by the API."""

	id: int
	name: str
	grade: str
	grade_type: str
	grade_subtype: str
	description: str
	is_active: bool
	academic_year: GradeAcademicYearSchema
	student_count: int

	@classmethod
	def from_model(cls, grade_obj, student_count: int = 0) -> GradeResponseSchema:
		return cls(
			id=grade_obj.pk,
			name=grade_obj.name,
			grade=grade_obj.grade,
			grade_type=grade_obj.grade_type,
			grade_subtype=grade_obj.grade_subtype,
			description=grade_obj.description,
			is_active=grade_obj.is_active,
			academic_year=GradeAcademicYearSchema.from_model(grade_obj.academic_year),
			student_count=student_count,
		)


class StudentEnrollSchema(BaseModel):
	"""Payload to enroll a student in a grade."""

	student_id: str = Field(..., description="UUID of the student user to enroll.")


class EnrollmentResponseSchema(BaseModel):
	"""Enrollment record returned by the API."""

	enrollment_id: int
	student_id: str
	grade_id: int
	academic_year_id: int
	joined_at: str

	@classmethod
	def from_model(cls, enrollment) -> EnrollmentResponseSchema:
		return cls(
			enrollment_id=enrollment.pk,
			student_id=str(enrollment.student_id),
			grade_id=enrollment.grade_id,
			academic_year_id=enrollment.academic_year_id,
			joined_at=enrollment.joined_at.isoformat(),
		)
