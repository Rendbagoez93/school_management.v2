from django.urls import path

from .views import (
	StaffHealthAPIView,
	StaffMemberListAPIView,
	TeacherDetailAPIView,
	TeacherListAPIView,
)

app_name = "staff-management-api"

urlpatterns = [
	path("health/", StaffHealthAPIView.as_view(), name="health"),
	path("staff/", StaffMemberListAPIView.as_view(), name="staff-list"),
	path("teachers/", TeacherListAPIView.as_view(), name="teacher-list"),
	path("teachers/<int:teacher_id>/", TeacherDetailAPIView.as_view(), name="teacher-detail"),
]
