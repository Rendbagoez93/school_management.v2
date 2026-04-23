"""Pydantic schemas for the academic_management API.

Defines request/response shapes for AcademicYear operations.
All inputs are validated here before reaching the service layer.
"""

from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator

_VALID_STATUSES = {"SETUP", "ENROLLMENT", "ACTIVE", "COMPLETED"}
_VALID_DEPLOYMENT_TYPES = {"FRESH_START", "MID_YEAR"}


class AcademicYearCreateSchema(BaseModel):
	"""Payload for creating a new AcademicYear."""

	name: str = Field(..., min_length=1, max_length=32)
	start_date: date
	end_date: date
	deployment_type: Literal["FRESH_START", "MID_YEAR"] = "FRESH_START"
	enrollment_start_date: date | None = None
	enrollment_end_date: date | None = None

	@model_validator(mode="after")
	def validate_dates(self) -> AcademicYearCreateSchema:
		if self.start_date >= self.end_date:
			raise ValueError("start_date must be before end_date.")
		return self


class AcademicYearUpdateSchema(BaseModel):
	"""Payload for partial update of an AcademicYear.

	Only supplied (non-None) fields are applied.
	"""

	name: str | None = Field(default=None, min_length=1, max_length=32)
	start_date: date | None = None
	end_date: date | None = None
	enrollment_start_date: date | None = None
	enrollment_end_date: date | None = None


class AcademicYearStatusUpdateSchema(BaseModel):
	"""Payload to transition an AcademicYear's status."""

	status: str

	@field_validator("status")
	@classmethod
	def validate_status(cls, v: str) -> str:
		if v not in _VALID_STATUSES:
			raise ValueError(f"Invalid status '{v}'. Must be one of: {', '.join(sorted(_VALID_STATUSES))}.")
		return v


class AcademicYearResponseSchema(BaseModel):
	"""Full AcademicYear representation returned by the API."""

	id: int
	name: str
	start_date: date
	end_date: date
	is_active: bool
	status: str
	status_display: str
	deployment_type: str
	deployment_type_display: str
	setup_completed: bool
	enrollment_start_date: date | None
	enrollment_end_date: date | None

	@classmethod
	def from_model(cls, year) -> AcademicYearResponseSchema:
		return cls(
			id=year.pk,
			name=year.name,
			start_date=year.start_date,
			end_date=year.end_date,
			is_active=year.is_active,
			status=year.status,
			status_display=year.get_status_display(),
			deployment_type=year.deployment_type,
			deployment_type_display=year.get_deployment_type_display(),
			setup_completed=year.setup_completed,
			enrollment_start_date=year.enrollment_start_date,
			enrollment_end_date=year.enrollment_end_date,
		)


class AcademicYearListQuerySchema(BaseModel):
	"""Query parameters for listing academic years."""

	status: str | None = None
	is_active: bool | None = None

	@field_validator("status")
	@classmethod
	def validate_status(cls, v: str | None) -> str | None:
		if v is not None and v not in _VALID_STATUSES:
			raise ValueError(f"Invalid status filter '{v}'. Must be one of: {', '.join(sorted(_VALID_STATUSES))}.")
		return v
