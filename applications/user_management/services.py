"""Service layer for user management operations.

This module contains business logic that was moved from models.py to follow
the separation of concerns principle. Models should only handle data structure
and persistence, while services handle business logic and validation.
"""

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from config.roles import RoleEnum

User = get_user_model()


class UserRoleService:
    @staticmethod
    def is_parent(user) -> bool:
        """Check if user has a Parent profile."""
        return hasattr(user, "parent") and user.parent is not None
    
    @staticmethod
    def is_student(user) -> bool:
        """Check if user has a Student profile."""
        return hasattr(user, "student") and user.student is not None
    
    @staticmethod
    def is_school_staff(user) -> bool:
        """Check if user has a SchoolStaff profile."""
        return hasattr(user, "schoolstaff") and user.schoolstaff is not None
    
    @staticmethod
    def is_principal(user) -> bool:
        """Check if user is a principal (has PRINCIPAL role and SchoolStaff profile)."""
        return (
            user.groups.filter(name=RoleEnum.PRINCIPAL.value).exists() 
            and UserRoleService.is_school_staff(user)
        )
    
    @staticmethod
    def is_vp(user) -> bool:
        """Check if user is a vice principal (has VP role and SchoolStaff profile)."""
        return (
            user.groups.filter(name=RoleEnum.VP.value).exists() 
            and UserRoleService.is_school_staff(user)
        )
    
    @staticmethod
    def is_teacher(user) -> bool:
        """Check if user is a teacher (has TEACHER role and SchoolStaff profile)."""
        return (
            user.groups.filter(name=RoleEnum.TEACHER.value).exists() 
            and UserRoleService.is_school_staff(user)
        )
    
    @staticmethod
    def get_user_role(user) -> str | None:
        return user.groups.first().name if user.groups.exists() else None
    
    @staticmethod
    def get_user_roles(user) -> list[str]:
        return list(user.groups.values_list('name', flat=True))
    
    @staticmethod
    def has_role(user, role: str) -> bool:
        return user.groups.filter(name=role).exists()
    
    @staticmethod
    def has_any_role(user, roles: list[str]) -> bool:
        return user.groups.filter(name__in=roles).exists()
    
    @staticmethod
    def has_all_roles(user, roles: list[str]) -> bool:
        """Check if user has all the specified roles.
      
        Returns:
            True if user has all the specified roles
        """
        user_roles = set(user.groups.values_list('name', flat=True))
        return all(role in user_roles for role in roles)


class ParentService:
    """Service for Parent-related operations with validation."""
    
    @staticmethod
    def validate_student_role(student) -> None:
        if not student.groups.filter(name=RoleEnum.STUDENT.value).exists():
            raise ValidationError(
                f"User {student.get_full_name()} must have STUDENT role to be added as a child."
            )
    
    @staticmethod
    def add_child_with_validation(parent, student):
        ParentService.validate_student_role(student)
        parent.add_child(student)
    
    @staticmethod
    def get_validated_children(parent):
        return parent.children.filter(groups__name=RoleEnum.STUDENT.value)
    
    @staticmethod
    def validate_all_children_have_student_role(parent) -> None:
        if parent.pk:
            invalid_children = parent.children.exclude(groups__name=RoleEnum.STUDENT.value)
            if invalid_children.exists():
                invalid_names = ", ".join(
                    invalid_children.values_list('email', flat=True)[:5]
                )
                raise ValidationError({
                    'children': f'All children must have STUDENT role. '
                               f'Invalid users: {invalid_names}'
                })


class TeacherProfileService:
    """Service for Teacher profile operations.

    Bridges user account creation (user_management) with Teacher professional
    profile creation (teacher_management). The underlying User + SchoolStaff
    profile must already exist before calling these methods.
    """

    @staticmethod
    def create_teacher_profile(
        user,
        employee_id: str,
        department: str = "",
        specialization: str = "",
        date_of_joining=None,
    ):
        """Create a Teacher profile for an existing user.

        Args:
            user: SchoolUser instance that already has the TEACHER role.
            employee_id: Unique employee identifier (required).
            department: Optional department name.
            specialization: Optional teaching specialization.
            date_of_joining: Optional date the teacher joined.

        Returns:
            Teacher instance.

        Raises:
            ValueError: If user doesn't have TEACHER role or already has a profile.
        """
        from applications.school_management.teacher_management.models import Teacher

        if not user.groups.filter(name=RoleEnum.TEACHER.value).exists():
            raise ValueError(f"User {user.get_full_name()} must have TEACHER role")

        if Teacher.objects.filter(user=user, is_deleted=False).exists():
            raise ValueError(f"User {user.get_full_name()} already has a Teacher profile")

        teacher = Teacher(
            user=user,
            employee_id=employee_id,
            department=department,
            specialization=specialization,
            date_of_joining=date_of_joining,
            is_active=True,
        )
        teacher.full_clean()
        teacher.save()
        return teacher

    @staticmethod
    def get_or_create_teacher_profile(
        user,
        employee_id: str,
        department: str = "",
        specialization: str = "",
        date_of_joining=None,
    ) -> tuple:
        """Get existing Teacher profile or create a new one.

        Args:
            user: SchoolUser instance that already has the TEACHER role.
            employee_id: Unique employee identifier used only when creating.
            department: Optional department name used only when creating.
            specialization: Optional teaching specialization used only when creating.
            date_of_joining: Optional date used only when creating.

        Returns:
            Tuple of (Teacher instance, created: bool).

        Raises:
            ValueError: If user doesn't have TEACHER role.
        """
        from applications.school_management.teacher_management.models import Teacher

        if not user.groups.filter(name=RoleEnum.TEACHER.value).exists():
            raise ValueError(f"User {user.get_full_name()} must have TEACHER role")

        existing = Teacher.objects.filter(user=user, is_deleted=False).first()
        if existing:
            return existing, False

        teacher = TeacherProfileService.create_teacher_profile(
            user=user,
            employee_id=employee_id,
            department=department,
            specialization=specialization,
            date_of_joining=date_of_joining,
        )
        return teacher, True
