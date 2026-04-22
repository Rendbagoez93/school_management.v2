"""API URL configuration aggregator for School Management System."""

from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    # API schema and documentation
    path("schema/", SpectacularAPIView.as_view(), name="api-schema"),
    path("docs/swagger/", SpectacularSwaggerView.as_view(url_name="api-schema"), name="api-docs-swagger"),
    path("docs/redoc/", SpectacularRedocView.as_view(url_name="api-schema"), name="api-docs-redoc"),

    # JWT token endpoints
    path("auth/token/", TokenObtainPairView.as_view(), name="token-obtain-pair"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),

    # Implemented app APIs
    path("staff-management/", include("applications.school_management.staff_management.urls")),
]
