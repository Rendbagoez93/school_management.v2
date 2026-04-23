"""Pydantic schemas for the staff_management API.

Defines request and response shapes for StaffMember operations.
All inputs are validated here before reaching the service layer.
"""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field, field_validator


class StaffMemberCreateSchema(BaseModel):
	"""Payload for creating a new StaffMember profile."""

	user_id: str = Field(..., description="UUID of the user account to attach this profile to.")
	employee_id: str = Field(..., min_length=1, max_length=32)
	department: str = Field(default="", max_length=100)
	job_title: str = Field(default="", max_length=100)
	date_of_joining: date | None = None

	@field_validator("employee_id")
	@classmethod
	def normalise_employee_id(cls, v: str) -> str:
		return v.strip().upper()


class StaffMemberUpdateSchema(BaseModel):
	"""Payload for partial update of a StaffMember profile.

	All fields are optional; only supplied fields are updated.
	"""

	department: str | None = Field(default=None, max_length=100)
	job_title: str | None = Field(default=None, max_length=100)
	date_of_joining: date | None = None


class StaffMemberDeactivateSchema(BaseModel):
	"""Payload to toggle the active status of a StaffMember."""

	is_active: bool


class StaffMemberUserSchema(BaseModel):
	"""Minimal user data embedded in StaffMember responses."""

	id: str
	email: str
	first_name: str
	last_name: str
	full_name: str

	@classmethod
	def from_user(cls, user) -> StaffMemberUserSchema:
		return cls(
			id=str(user.pk),
			email=user.email,
			first_name=user.first_name or "",
			last_name=user.last_name or "",
			full_name=user.get_full_name(),
		)


class StaffMemberResponseSchema(BaseModel):
	"""Full StaffMember representation returned by the API."""

	id: int
	employee_id: str
	department: str
	job_title: str
	date_of_joining: date | None
	is_active: bool
	user: StaffMemberUserSchema

	@classmethod
	def from_model(cls, member) -> StaffMemberResponseSchema:
		return cls(
			id=member.pk,
			employee_id=member.employee_id,
			department=member.department,
			job_title=member.job_title,
			date_of_joining=member.date_of_joining,
			is_active=member.is_active,
			user=StaffMemberUserSchema.from_user(member.user),
		)


class StaffMemberListQuerySchema(BaseModel):
	"""Query parameters for listing staff members."""

	department: str | None = None
	is_active: bool | None = None
	search: str | None = Field(default=None, max_length=100)
