"""User Management Application.

This application handles all user-related functionality including:
- User models (SchoolUser, Parent, Student, SchoolStaff)
- User role management and services
- User validators and DTOs
- Repository pattern for read/write operations

Public API:
    Models: SchoolUser, Parent, Student, SchoolStaff
    Services: UserRoleService, ParentService, TeacherProfileService
    Validators: PrincipalSetupForm
    DTOs: StaffMetrics
    Repository: get_staff_metrics, create_principal_user, create_staff_user
"""

# Models
from applications.user_management.models import (
    Parent,
    SchoolStaff,
    SchoolUser,
    Student,
)

# Services
from applications.user_management.services import (
    ParentService,
    TeacherProfileService,
    UserRoleService,
)

# Validators
from applications.user_management.validators import PrincipalSetupForm

# DTOs (Plain Old Python Objects)
from applications.user_management.pojo import StaffMetrics

# Repository layer
from applications.user_management.repo import (
    create_principal_user,
    create_staff_user,
    get_staff_metrics,
)

__all__ = [
    # Models
    "SchoolUser",
    "Parent",
    "Student",
    "SchoolStaff",
    # Services
    "UserRoleService",
    "ParentService",
    "TeacherProfileService",
    # Validators
    "PrincipalSetupForm",
    # DTOs
    "StaffMetrics",
    # Repository
    "get_staff_metrics",
    "create_principal_user",
    "create_staff_user",
]

default_app_config = "applications.user_management.apps.UserManagementConfig"
