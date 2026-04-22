from pydantic import BaseModel
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from shared.api import ApiError, api_list_response, api_response, parse_query

from .models import StaffMember, Teacher


class StaffQuerySchema(BaseModel):
	department: str | None = None


class TeacherQuerySchema(BaseModel):
	department: str | None = None


class StaffHealthAPIView(APIView):
	permission_classes = [IsAuthenticated]

	def get(self, request):
		return api_response({"service": "staff_management", "status": "ok"})


class StaffMemberListAPIView(APIView):
	permission_classes = [IsAuthenticated]

	def get(self, request):
		params = parse_query(request, StaffQuerySchema)

		queryset = StaffMember.objects.select_related("user").filter(is_active=True)
		if params.department:
			queryset = queryset.filter(department__iexact=params.department)

		results = [
			{
				"id": member.id,
				"employeeId": member.employee_id,
				"department": member.department,
				"jobTitle": member.job_title,
				"dateOfJoining": member.date_of_joining,
				"user": {
					"id": str(member.user_id),
					"email": member.user.email,
					"firstName": member.user.first_name,
					"lastName": member.user.last_name,
				},
			}
			for member in queryset
		]
		return api_list_response(results)


class TeacherListAPIView(APIView):
	permission_classes = [IsAuthenticated]

	def get(self, request):
		params = parse_query(request, TeacherQuerySchema)

		queryset = Teacher.objects.select_related("user").filter(is_active=True)
		if params.department:
			queryset = queryset.filter(department__iexact=params.department)

		results = [
			{
				"id": teacher.id,
				"employeeId": teacher.employee_id,
				"department": teacher.department,
				"specialization": teacher.specialization,
				"dateOfJoining": teacher.date_of_joining,
				"user": {
					"id": str(teacher.user_id),
					"email": teacher.user.email,
					"firstName": teacher.user.first_name,
					"lastName": teacher.user.last_name,
				},
			}
			for teacher in queryset
		]
		return api_list_response(results)


class TeacherDetailAPIView(APIView):
	permission_classes = [IsAuthenticated]

	def get(self, request, teacher_id: int):
		teacher = Teacher.objects.select_related("user").filter(pk=teacher_id, is_active=True).first()
		if not teacher:
			raise ApiError("not_found", "Teacher not found.", status=404)

		return api_response(
			{
				"id": teacher.id,
				"employeeId": teacher.employee_id,
				"department": teacher.department,
				"specialization": teacher.specialization,
				"dateOfJoining": teacher.date_of_joining,
				"user": {
					"id": str(teacher.user_id),
					"email": teacher.user.email,
					"firstName": teacher.user.first_name,
					"lastName": teacher.user.last_name,
				},
			}
		)
