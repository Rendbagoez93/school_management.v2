"""API views for the staff_management module.

Provides CRUD endpoints for StaffMember profiles.
All validation is delegated to Pydantic schemas; business logic
lives in StaffMemberService.
"""

from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from shared.api import ApiError, api_list_response, api_response, parse_body, parse_query

from .schemas import (
	StaffMemberCreateSchema,
	StaffMemberDeactivateSchema,
	StaffMemberListQuerySchema,
	StaffMemberResponseSchema,
	StaffMemberUpdateSchema,
)
from .services import StaffMemberService


class StaffHealthAPIView(APIView):
	permission_classes = [IsAuthenticated]

	def get(self, request):
		return api_response({"service": "staff_management", "status": "ok"})


class StaffMemberListCreateAPIView(APIView):
	"""GET list / POST create staff members."""

	permission_classes = [IsAuthenticated]

	def get(self, request):
		params = parse_query(request, StaffMemberListQuerySchema)
		queryset = StaffMemberService.list_staff(
			department=params.department,
			is_active=params.is_active,
			search=params.search,
		)
		results = [StaffMemberResponseSchema.from_model(m).model_dump(mode="json") for m in queryset]
		return api_list_response(results)

	def post(self, request):
		data = parse_body(request, StaffMemberCreateSchema)
		member = StaffMemberService.create(data)
		return api_response(
			StaffMemberResponseSchema.from_model(member).model_dump(mode="json"),
			code="created",
			msg="Staff member profile created.",
			status=201,
		)


class StaffMemberDetailAPIView(APIView):
	"""GET / PATCH / DELETE a single staff member."""

	permission_classes = [IsAuthenticated]

	def _get_or_404(self, staff_id: int):
		member = StaffMemberService.get_by_id(staff_id)
		if member is None:
			raise ApiError("not_found", "Staff member not found.", status=404)
		return member

	def get(self, request, staff_id: int):
		member = self._get_or_404(staff_id)
		return api_response(StaffMemberResponseSchema.from_model(member).model_dump(mode="json"))

	def patch(self, request, staff_id: int):
		member = self._get_or_404(staff_id)
		data = parse_body(request, StaffMemberUpdateSchema)
		updated = StaffMemberService.update(member, data)
		return api_response(StaffMemberResponseSchema.from_model(updated).model_dump(mode="json"))

	def delete(self, request, staff_id: int):
		member = self._get_or_404(staff_id)
		StaffMemberService.delete(member)
		return api_response(None, code="deleted", msg="Staff member deleted.", status=200)


class StaffMemberActivationAPIView(APIView):
	"""PATCH to activate or deactivate a staff member."""

	permission_classes = [IsAuthenticated]

	def patch(self, request, staff_id: int):
		member = StaffMemberService.get_by_id(staff_id)
		if member is None:
			raise ApiError("not_found", "Staff member not found.", status=404)
		data = parse_body(request, StaffMemberDeactivateSchema)
		updated = StaffMemberService.set_active(member, is_active=data.is_active)
		return api_response(StaffMemberResponseSchema.from_model(updated).model_dump(mode="json"))
