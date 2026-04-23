from django.urls import path

from .views import (
	AcademicYearDetailAPIView,
	AcademicYearHealthAPIView,
	AcademicYearListCreateAPIView,
	AcademicYearStatusAPIView,
)

app_name = "academic-management-api"

urlpatterns = [
	path("health/", AcademicYearHealthAPIView.as_view(), name="health"),
	path("", AcademicYearListCreateAPIView.as_view(), name="year-list-create"),
	path("<int:year_id>/", AcademicYearDetailAPIView.as_view(), name="year-detail"),
	path("<int:year_id>/status/", AcademicYearStatusAPIView.as_view(), name="year-status"),
]
