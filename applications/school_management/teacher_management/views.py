"""API views for the teacher_management module.

Provides CRUD endpoints for Teacher profiles.
Validation is handled by Pydantic schemas; business logic in TeacherService.
"""

from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from shared.api import ApiError, api_list_response, api_response, parse_body, parse_query

from .schemas import (
	TeacherCreateSchema,
	TeacherDeactivateSchema,
	TeacherListQuerySchema,
	TeacherResponseSchema,
	TeacherUpdateSchema,
)
from .services import TeacherService


class TeacherHealthAPIView(APIView):
	permission_classes = [IsAuthenticated]

	def get(self, request):
		return api_response({"service": "teacher_management", "status": "ok"})


class TeacherListCreateAPIView(APIView):
	"""GET list / POST create teacher profiles."""

	permission_classes = [IsAuthenticated]

	def get(self, request):
		params = parse_query(request, TeacherListQuerySchema)
		queryset = TeacherService.list_teachers(
			department=params.department,
			specialization=params.specialization,
			is_active=params.is_active,
			search=params.search,
		)
		results = [TeacherResponseSchema.from_model(t).model_dump(mode="json") for t in queryset]
		return api_list_response(results)

	def post(self, request):
		data = parse_body(request, TeacherCreateSchema)
		teacher = TeacherService.create(data)
		return api_response(
			TeacherResponseSchema.from_model(teacher).model_dump(mode="json"),
			code="created",
			msg="Teacher profile created.",
			status=201,
		)


class TeacherDetailAPIView(APIView):
	"""GET / PATCH / DELETE a single teacher profile."""

	permission_classes = [IsAuthenticated]

	def _get_or_404(self, teacher_id: int) -> object:
		teacher = TeacherService.get_by_id(teacher_id)
		if teacher is None:
			raise ApiError("not_found", "Teacher not found.", status=404)
		return teacher

	def get(self, request, teacher_id: int):
		teacher = self._get_or_404(teacher_id)
		return api_response(TeacherResponseSchema.from_model(teacher).model_dump(mode="json"))

	def patch(self, request, teacher_id: int):
		teacher = self._get_or_404(teacher_id)
		data = parse_body(request, TeacherUpdateSchema)
		updated = TeacherService.update(teacher, data)
		return api_response(TeacherResponseSchema.from_model(updated).model_dump(mode="json"))

	def delete(self, request, teacher_id: int):
		teacher = self._get_or_404(teacher_id)
		TeacherService.delete(teacher)
		return api_response(None, code="deleted", msg="Teacher profile deleted.", status=200)


class TeacherActivationAPIView(APIView):
	"""PATCH to activate or deactivate a teacher profile."""

	permission_classes = [IsAuthenticated]

	def patch(self, request, teacher_id: int):
		teacher = TeacherService.get_by_id(teacher_id)
		if teacher is None:
			raise ApiError("not_found", "Teacher not found.", status=404)
		data = parse_body(request, TeacherDeactivateSchema)
		updated = TeacherService.set_active(teacher, is_active=data.is_active)
		return api_response(TeacherResponseSchema.from_model(updated).model_dump(mode="json"))
