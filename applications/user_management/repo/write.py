"""Write operations for user management."""

from applications.user_management.models import SchoolUser
from applications.user_management.validators import PrincipalSetupForm
from config.roles import RoleEnum


def create_principal_user(principal_data: PrincipalSetupForm) -> "SchoolUser":
    """Create a principal user account."""
    # Create the user
    user = SchoolUser.objects.create_principal(
        **principal_data.model_dump(exclude={"confirm_password"}),
    )
    return user


def create_staff_user(role: RoleEnum, user_data: dict) -> "SchoolUser":
    match role:
        case RoleEnum.TEACHER:
            user = SchoolUser.objects.create_teacher(**user_data)
        case RoleEnum.VP:
            user = SchoolUser.objects.create_vp(**user_data)
        case RoleEnum.STAFF:
            user = SchoolUser.objects.create_staffuser(**user_data)
        case _:
            raise ValueError(f"Unsupported role: {role}")
    return user
