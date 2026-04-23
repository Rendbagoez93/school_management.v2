"""API views for the grade_management module.

Provides CRUD endpoints for Grades and student enrollment management.
Validation is delegated to Pydantic schemas; business logic lives in GradeService.
"""

from django.core.exceptions import ValidationError
from django.db.models import Count
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from applications.school_management.academic_management.models import StudentEnrollment
from shared.api import ApiError, api_list_response, api_response, parse_body, parse_query

from .schemas import (
	EnrollmentResponseSchema,
	GradeCreateSchema,
	GradeListQuerySchema,
	GradeResponseSchema,
	GradeUpdateSchema,
	StudentEnrollSchema,
)
from .services import GradeService


class GradeHealthAPIView(APIView):
	permission_classes = [IsAuthenticated]

	def get(self, request):
		return api_response({"service": "grade_management", "status": "ok"})


class GradeListCreateAPIView(APIView):
	"""GET list / POST create grades."""

	permission_classes = [IsAuthenticated]

	def get(self, request):
		params = parse_query(request, GradeListQuerySchema)
		queryset = GradeService.list_grades(
			academic_year_id=params.academic_year_id,
			grade=params.grade,
			is_active=params.is_active,
			search=params.search,
		)

		# Build student_count per grade in a single query (avoids N+1)
		grade_ids = list(queryset.values_list("id", flat=True))
		counts: dict[int, int] = {
			row["grade_id"]: row["cnt"]
			for row in (
				StudentEnrollment.objects.filter(grade_id__in=grade_ids, is_deleted=False)
				.values("grade_id")
				.annotate(cnt=Count("id"))
			)
		}

		results = [
			GradeResponseSchema.from_model(g, student_count=counts.get(g.pk, 0)).model_dump(mode="json")
			for g in queryset
		]
		return api_list_response(results)

	def post(self, request):
		data = parse_body(request, GradeCreateSchema)
		grade_obj = GradeService.create(data)
		return api_response(
			GradeResponseSchema.from_model(grade_obj).model_dump(mode="json"),
			code="created",
			msg="Grade created.",
			status=201,
		)


class GradeDetailAPIView(APIView):
	"""GET / PATCH / DELETE a single grade."""

	permission_classes = [IsAuthenticated]

	def _get_or_404(self, grade_id: int) -> object:
		grade_obj = GradeService.get_by_id(grade_id)
		if grade_obj is None:
			raise ApiError("not_found", "Grade not found.", status=404)
		return grade_obj

	def get(self, request, grade_id: int):
		grade_obj = self._get_or_404(grade_id)
		count = StudentEnrollment.objects.filter(grade=grade_obj, is_deleted=False).count()
		return api_response(GradeResponseSchema.from_model(grade_obj, student_count=count).model_dump(mode="json"))

	def patch(self, request, grade_id: int):
		grade_obj = self._get_or_404(grade_id)
		data = parse_body(request, GradeUpdateSchema)
		updated = GradeService.update(grade_obj, data)
		count = StudentEnrollment.objects.filter(grade=updated, is_deleted=False).count()
		return api_response(GradeResponseSchema.from_model(updated, student_count=count).model_dump(mode="json"))

	def delete(self, request, grade_id: int):
		grade_obj = self._get_or_404(grade_id)
		GradeService.delete(grade_obj)
		return api_response(None, code="deleted", msg="Grade deleted.", status=200)


class GradeStudentListCreateAPIView(APIView):
	"""GET students enrolled in a grade / POST to enroll a student."""

	permission_classes = [IsAuthenticated]

	def _get_grade_or_404(self, grade_id: int) -> object:
		grade_obj = GradeService.get_by_id(grade_id)
		if grade_obj is None:
			raise ApiError("not_found", "Grade not found.", status=404)
		return grade_obj

	def get(self, request, grade_id: int):
		grade_obj = self._get_grade_or_404(grade_id)
		enrollments = (
			StudentEnrollment.objects.filter(grade=grade_obj, is_deleted=False)
			.select_related("student")
			.order_by("joined_at")
		)
		results = [EnrollmentResponseSchema.from_model(e).model_dump(mode="json") for e in enrollments]
		return api_list_response(results)

	def post(self, request, grade_id: int):
		grade_obj = self._get_grade_or_404(grade_id)
		data = parse_body(request, StudentEnrollSchema)
		try:
			enrollment = GradeService.enroll_student(grade_obj, data.student_id)
		except ValidationError as exc:
			raise ApiError("validation_error", str(next(iter(exc.message_dict.values()))[0]), status=422)
		return api_response(
			EnrollmentResponseSchema.from_model(enrollment).model_dump(mode="json"),
			code="created",
			msg="Student enrolled.",
			status=201,
		)


class GradeStudentDetailAPIView(APIView):
	"""DELETE to unenroll a student from a grade."""

	permission_classes = [IsAuthenticated]

	def delete(self, request, grade_id: int, student_id: str):
		if GradeService.get_by_id(grade_id) is None:
			raise ApiError("not_found", "Grade not found.", status=404)
		try:
			GradeService.unenroll_student(grade_id, student_id)
		except ValidationError:
			raise ApiError("not_found", "Enrollment not found.", status=404)
		return api_response(None, code="deleted", msg="Student unenrolled.", status=200)

