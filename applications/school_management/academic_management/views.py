"""API views for the academic_management module.

Provides CRUD + status-transition endpoints for AcademicYear.
Validation is delegated to Pydantic schemas; business logic lives in AcademicYearService.
"""

from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from shared.api import ApiError, api_list_response, api_response, parse_body, parse_query

from .schemas import (
	AcademicYearCreateSchema,
	AcademicYearListQuerySchema,
	AcademicYearResponseSchema,
	AcademicYearStatusUpdateSchema,
	AcademicYearUpdateSchema,
)
from .services import AcademicYearService


class AcademicYearHealthAPIView(APIView):
	permission_classes = [IsAuthenticated]

	def get(self, request):
		return api_response({"service": "academic_management", "status": "ok"})


class AcademicYearListCreateAPIView(APIView):
	"""GET list / POST create academic years."""

	permission_classes = [IsAuthenticated]

	def get(self, request):
		params = parse_query(request, AcademicYearListQuerySchema)
		queryset = AcademicYearService.list_years(
			status=params.status,
			is_active=params.is_active,
		)
		results = [AcademicYearResponseSchema.from_model(y).model_dump(mode="json") for y in queryset]
		return api_list_response(results)

	def post(self, request):
		data = parse_body(request, AcademicYearCreateSchema)
		year = AcademicYearService.create(data)
		return api_response(
			AcademicYearResponseSchema.from_model(year).model_dump(mode="json"),
			code="created",
			msg="Academic year created.",
			status=201,
		)


class AcademicYearDetailAPIView(APIView):
	"""GET / PATCH / DELETE a single academic year."""

	permission_classes = [IsAuthenticated]

	def _get_or_404(self, year_id: int) -> object:
		year = AcademicYearService.get_by_id(year_id)
		if year is None:
			raise ApiError("not_found", "Academic year not found.", status=404)
		return year

	def get(self, request, year_id: int):
		year = self._get_or_404(year_id)
		return api_response(AcademicYearResponseSchema.from_model(year).model_dump(mode="json"))

	def patch(self, request, year_id: int):
		year = self._get_or_404(year_id)
		data = parse_body(request, AcademicYearUpdateSchema)
		updated = AcademicYearService.update(year, data)
		return api_response(AcademicYearResponseSchema.from_model(updated).model_dump(mode="json"))

	def delete(self, request, year_id: int):
		year = self._get_or_404(year_id)
		AcademicYearService.delete(year)
		return api_response(None, code="deleted", msg="Academic year deleted.", status=200)


class AcademicYearStatusAPIView(APIView):
	"""PATCH to transition an academic year's status."""

	permission_classes = [IsAuthenticated]

	def patch(self, request, year_id: int):
		year = AcademicYearService.get_by_id(year_id)
		if year is None:
			raise ApiError("not_found", "Academic year not found.", status=404)
		data = parse_body(request, AcademicYearStatusUpdateSchema)
		updated = AcademicYearService.transition_status(year, data.status)
		return api_response(AcademicYearResponseSchema.from_model(updated).model_dump(mode="json"))

