"""API URL configuration aggregator for School Management System.

All API routes are mounted under /api/ prefix.
This file aggregates all app-specific API routes.
"""

from django.urls import include, path

urlpatterns = [
    # Auth endpoints will be added here
    # path("auth/", include("applications.auth.api_urls")),
    
    # Academic management
    # path("academic/", include("applications.school_management.academic_management.api_urls")),
    
    # Students
    # path("students/", include("applications.school_management.student_management.api_urls")),
    
    # Parents
    # path("parent/", include("applications.school_management.parent_management.api_urls")),
    
    # Placeholder - add API routes as apps are implemented
]
