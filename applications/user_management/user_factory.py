"""
User Factory - Centralized user and profile creation.

This module provides a single factory for creating users with their associated
profiles and roles, eliminating duplication in SchoolUserManager.
"""

from django.contrib.auth.models import Group
from django.db import transaction

from config.roles import RoleEnum

from .profile_rules import (
    ProfileType,
    get_required_profile_type,
    validate_role_profile_consistency,
)


class UserCreationError(Exception):
    """Raised when user creation fails validation or execution."""
    pass


class UserProfileFactory:
    """
    Factory for creating users with profiles and roles.
    
    This centralizes all user creation logic that was previously duplicated
    across multiple SchoolUserManager methods.
    """
    
    def __init__(self, user_manager):
        """
        Initialize factory with a user manager instance.
        
        Args:
            user_manager: SchoolUserManager instance for user creation
        """
        self.user_manager = user_manager
    
    @transaction.atomic
    def create_user_with_profile(
        self,
        role: RoleEnum,
        is_staff_user: bool = False,
        create_teacher_profile: bool = False,
        **user_data
    ):
        """
        Create a user with appropriate profile and role.
        
        Args:
            role: The role to assign to the user
            is_staff_user: If True, creates a staff user (has staff privileges)
            create_teacher_profile: If True and role is TEACHER, creates Teacher model
            **user_data: Additional user data (email, first_name, etc.)
            
        Returns:
            Created user instance
            
        Raises:
            UserCreationError: If validation fails or creation encounters errors
        """
        # Get the group for this role
        try:
            group = Group.objects.get(name=role.value)
        except Group.DoesNotExist:
            raise UserCreationError(f"Role group '{role.value}' does not exist")
        
        # Determine required profile type
        try:
            profile_type = get_required_profile_type(role)
        except ValueError as e:
            raise UserCreationError(str(e))
        
        # Validate role-profile consistency
        is_valid, error_msg = validate_role_profile_consistency(
            roles={role},
            profile_types={profile_type}
        )
        if not is_valid:
            raise UserCreationError(f"Role-profile validation failed: {error_msg}")
        
        # Create base user (staff or regular)
        if is_staff_user:
            user = self.user_manager.create_staffuser(**user_data)
        else:
            user = self.user_manager.create_user(**user_data)
        
        # Create appropriate profile
        try:
            self._create_profile(user, profile_type)
        except Exception as e:
            raise UserCreationError(f"Failed to create profile: {e}")
        
        # Assign role
        group.user_set.add(user)
        
        # Special case: Create Teacher model for timetable functionality
        if role == RoleEnum.TEACHER and create_teacher_profile:
            self._create_teacher_model(user)
        
        return user
    
    def _create_profile(self, user, profile_type: ProfileType):
        """
        Create the appropriate profile for a user.
        
        Args:
            user: The user instance
            profile_type: The type of profile to create
            
        Returns:
            Created profile instance
        """
        # Import here to avoid circular imports
        from .models import Parent, SchoolStaff, Student
        
        profile_class_map = {
            ProfileType.PARENT: Parent,
            ProfileType.STUDENT: Student,
            ProfileType.SCHOOL_STAFF: SchoolStaff,
        }
        
        profile_class = profile_class_map.get(profile_type)
        if not profile_class:
            raise UserCreationError(f"Unknown profile type: {profile_type}")
        
        return profile_class.objects.create(user=user)
    
    def _create_teacher_model(self, user):
        """
        Create Teacher model for academic functionality.
        
        This is separate from SchoolStaff profile and used for
        timetable, subject assignments, etc.
        
        Args:
            user: The user instance (must have TEACHER role)
        """
        from applications.school_management.staff_management.models import Teacher
        
        # Validate user has teacher role
        if not user.groups.filter(name=RoleEnum.TEACHER.value).exists():
            raise UserCreationError(
                f"User {user.get_full_name()} must have TEACHER role"
            )
        
        # Check if Teacher model already exists
        existing_teacher = Teacher.objects.filter(email=user.email).first()
        if existing_teacher:
            return existing_teacher
        
        # Create new Teacher model
        teacher = Teacher.objects.create(
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            phone_number=getattr(user, 'phone_number', ''),
            is_active=user.is_active
        )
        
        return teacher


# Convenience factory functions for common user types

def create_principal(user_manager, **user_data):
    """Create a principal user with SchoolStaff profile."""
    factory = UserProfileFactory(user_manager)
    return factory.create_user_with_profile(
        role=RoleEnum.PRINCIPAL,
        is_staff_user=True,
        **user_data
    )


def create_vp(user_manager, **user_data):
    """Create a vice principal user with SchoolStaff profile."""
    factory = UserProfileFactory(user_manager)
    return factory.create_user_with_profile(
        role=RoleEnum.VP,
        is_staff_user=True,
        **user_data
    )


def create_teacher(user_manager, create_profile=False, **user_data):
    """
    Create a teacher user with SchoolStaff profile.
    
    Args:
        user_manager: SchoolUserManager instance
        create_profile: If True, also creates Teacher model for academic functions
        **user_data: User data
    """
    factory = UserProfileFactory(user_manager)
    return factory.create_user_with_profile(
        role=RoleEnum.TEACHER,
        is_staff_user=True,
        create_teacher_profile=create_profile,
        **user_data
    )


def create_staff(user_manager, **user_data):
    """Create a staff user with SchoolStaff profile."""
    factory = UserProfileFactory(user_manager)
    return factory.create_user_with_profile(
        role=RoleEnum.STAFF,
        is_staff_user=True,
        **user_data
    )


def create_student(user_manager, **user_data):
    """Create a student user with Student profile."""
    factory = UserProfileFactory(user_manager)
    return factory.create_user_with_profile(
        role=RoleEnum.STUDENT,
        is_staff_user=False,
        **user_data
    )


def create_parent(user_manager, **user_data):
    """Create a parent user with Parent profile."""
    factory = UserProfileFactory(user_manager)
    return factory.create_user_with_profile(
        role=RoleEnum.PARENT,
        is_staff_user=False,
        **user_data
    )
