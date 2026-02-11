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
                    invalid_children.values_list('username', flat=True)[:5]
                )
                raise ValidationError({
                    'children': f'All children must have STUDENT role. '
                               f'Invalid users: {invalid_names}'
                })


class TeacherProfileService:
    """Service for Teacher profile operations.
    
    NOTE: This service is prepared for future Teacher model implementation.
    The teacher_management app and Teacher model do not currently exist.
    
    When implementing the Teacher model:
    1. Create applications.school_management.teacher_management app
    2. Define Teacher model with appropriate fields
    3. Uncomment the import statements in the methods below
    4. Update this service to handle Teacher profile creation/management
    
    Handles creation and management of Teacher profiles to avoid duplication
    and maintain separation of concerns.
    """
    
    @staticmethod
    def create_teacher_profile(user):
        """Create a Teacher profile for a user with validation.
        
        NOTE: Teacher model not yet implemented. This is a placeholder.
        
        Args:
            user: SchoolUser instance with TEACHER role
        
        Returns:
            Teacher instance (when teacher_management app is created)
        
        Raises:
            ValueError: If user doesn't have TEACHER role
            NotImplementedError: Teacher model doesn't exist yet
        """
        # Validate user has teacher role
        if not user.groups.filter(name=RoleEnum.TEACHER.value).exists():
            raise ValueError(f"User {user.get_full_name()} must have TEACHER role")
        
        raise NotImplementedError(
            "Teacher model not yet implemented. "
            "Create applications.school_management.teacher_management app first."
        )
        
        # TODO: Uncomment when Teacher model is implemented
        # from applications.school_management.teacher_management.models import Teacher
        # 
        # # Check if Teacher profile already exists
        # existing_teacher = Teacher.objects.filter(email=user.email).first()
        # if existing_teacher:
        #     # Return existing instead of creating duplicate
        #     return existing_teacher
        # 
        # # Create new Teacher profile
        # teacher = Teacher.objects.create(
        #     first_name=user.first_name,
        #     last_name=user.last_name,
        #     email=user.email,
        #     phone_number=getattr(user, 'phone_number', ''),
        #     is_active=user.is_active
        # )
        # 
        # return teacher
    
    @staticmethod
    def get_or_create_teacher_profile(user):
        """Get existing Teacher profile or create new one.
        
        NOTE: Teacher model not yet implemented. This is a placeholder.
        
        Args:
            user: SchoolUser instance with TEACHER role
        
        Returns:
            Tuple of (Teacher instance, created: bool)
        
        Raises:
            ValueError: If user doesn't have TEACHER role
            NotImplementedError: Teacher model doesn't exist yet
        """
        # Validate user has teacher role
        if not user.groups.filter(name=RoleEnum.TEACHER.value).exists():
            raise ValueError(f"User {user.get_full_name()} must have TEACHER role")
        
        raise NotImplementedError(
            "Teacher model not yet implemented. "
            "Create applications.school_management.teacher_management app first."
        )
        
        # TODO: Uncomment when Teacher model is implemented
        # from applications.school_management.teacher_management.models import Teacher
        # 
        # # Try to get existing teacher profile
        # existing_teacher = Teacher.objects.filter(email=user.email).first()
        # if existing_teacher:
        #     return existing_teacher, False
        # 
        # # Create new Teacher profile
        # teacher = Teacher.objects.create(
        #     first_name=user.first_name,
        #     last_name=user.last_name,
        #     email=user.email,
        #     phone_number=getattr(user, 'phone_number', ''),
        #     is_active=user.is_active
        # )
        # 
        # return teacher, True
