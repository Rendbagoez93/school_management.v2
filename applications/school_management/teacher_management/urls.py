from django.urls import path

from .views import (
	TeacherActivationAPIView,
	TeacherDetailAPIView,
	TeacherHealthAPIView,
	TeacherListCreateAPIView,
)

app_name = "teacher-management-api"

urlpatterns = [
	path("health/", TeacherHealthAPIView.as_view(), name="health"),
	path("", TeacherListCreateAPIView.as_view(), name="teacher-list-create"),
	path("<int:teacher_id>/", TeacherDetailAPIView.as_view(), name="teacher-detail"),
	path("<int:teacher_id>/activation/", TeacherActivationAPIView.as_view(), name="teacher-activation"),
]
