from django.urls import path

from .views import (
	StaffHealthAPIView,
	StaffMemberActivationAPIView,
	StaffMemberDetailAPIView,
	StaffMemberListCreateAPIView,
)

app_name = "staff-management-api"

urlpatterns = [
	path("health/", StaffHealthAPIView.as_view(), name="health"),
	path("", StaffMemberListCreateAPIView.as_view(), name="staff-list-create"),
	path("<int:staff_id>/", StaffMemberDetailAPIView.as_view(), name="staff-detail"),
	path("<int:staff_id>/activation/", StaffMemberActivationAPIView.as_view(), name="staff-activation"),
]
