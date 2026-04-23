"""Pydantic schemas for the teacher_management API.

Defines request and response shapes for Teacher profile operations.
"""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field, field_validator


class TeacherCreateSchema(BaseModel):
	"""Payload for creating a new Teacher profile."""

	user_id: str = Field(..., description="UUID of the user account (must have Teacher role).")
	employee_id: str = Field(..., min_length=1, max_length=32)
	department: str = Field(default="", max_length=100)
	specialization: str = Field(default="", max_length=120)
	date_of_joining: date | None = None

	@field_validator("employee_id")
	@classmethod
	def normalise_employee_id(cls, v: str) -> str:
		return v.strip().upper()


class TeacherUpdateSchema(BaseModel):
	"""Payload for partial update of a Teacher profile.

	Only supplied fields are applied.
	"""

	department: str | None = Field(default=None, max_length=100)
	specialization: str | None = Field(default=None, max_length=120)
	date_of_joining: date | None = None


class TeacherDeactivateSchema(BaseModel):
	"""Payload to toggle the active status of a Teacher."""

	is_active: bool


class TeacherUserSchema(BaseModel):
	"""Minimal user data embedded in Teacher responses."""

	id: str
	email: str
	first_name: str
	last_name: str
	full_name: str

	@classmethod
	def from_user(cls, user) -> TeacherUserSchema:
		return cls(
			id=str(user.pk),
			email=user.email,
			first_name=user.first_name or "",
			last_name=user.last_name or "",
			full_name=user.get_full_name(),
		)


class TeacherResponseSchema(BaseModel):
	"""Full Teacher representation returned by the API."""

	id: int
	employee_id: str
	department: str
	specialization: str
	date_of_joining: date | None
	is_active: bool
	user: TeacherUserSchema

	@classmethod
	def from_model(cls, teacher) -> TeacherResponseSchema:
		return cls(
			id=teacher.pk,
			employee_id=teacher.employee_id,
			department=teacher.department,
			specialization=teacher.specialization,
			date_of_joining=teacher.date_of_joining,
			is_active=teacher.is_active,
			user=TeacherUserSchema.from_user(teacher.user),
		)


class TeacherListQuerySchema(BaseModel):
	"""Query parameters for listing teachers."""

	department: str | None = None
	specialization: str | None = None
	is_active: bool | None = None
	search: str | None = Field(default=None, max_length=100)
