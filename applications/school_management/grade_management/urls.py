from django.urls import path

from .views import (
	GradeDetailAPIView,
	GradeHealthAPIView,
	GradeListCreateAPIView,
	GradeStudentDetailAPIView,
	GradeStudentListCreateAPIView,
)

app_name = "grade-management-api"

urlpatterns = [
	path("health/", GradeHealthAPIView.as_view(), name="health"),
	path("", GradeListCreateAPIView.as_view(), name="grade-list-create"),
	path("<int:grade_id>/", GradeDetailAPIView.as_view(), name="grade-detail"),
	path("<int:grade_id>/students/", GradeStudentListCreateAPIView.as_view(), name="grade-students"),
	path("<int:grade_id>/students/<str:student_id>/", GradeStudentDetailAPIView.as_view(), name="grade-student-detail"),
]
