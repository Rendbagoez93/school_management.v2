from typing import Union

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, models, transaction

from config.roles import RoleEnum
from modules.user.models import DefaultUserManager
from shared.base_models import TimeStampedModel

from .profile_rules import (
    ProfileType,
    validate_profile_combination,
    validate_role_profile_consistency,
)

User = get_user_model()
ProfileClass = Union["Parent", "Student", "SchoolStaff"]


class SchoolUserManager(DefaultUserManager):
    """Manager for SchoolUser with factory-based user creation."""
    
    def all_staff(self):
        """Return all staff users in the school management system."""
        return self.filter(groups__name__in=RoleEnum.staff_roles()).prefetch_related("groups")

    def get_teachers(self):
        return self.filter(groups__name=RoleEnum.TEACHER.value)

    def get_students(self):
        return self.filter(groups__name=RoleEnum.STUDENT.value)

    def get_parents(self):
        return self.filter(groups__name=RoleEnum.PARENT.value)

    def get_principals(self):
        return self.filter(groups__name=RoleEnum.PRINCIPAL.value)

    @transaction.atomic
    def create_principal(self, **user_data):
        """Create principal using factory."""
        from .user_factory import create_principal
        return create_principal(self, **user_data)

    @transaction.atomic
    def create_vp(self, **user_data):
        """Create vice principal using factory."""
        from .user_factory import create_vp
        return create_vp(self, **user_data)

    @transaction.atomic
    def create_parent(self, **user_data):
        """Create parent using factory."""
        from .user_factory import create_parent
        return create_parent(self, **user_data)

    @transaction.atomic
    def create_student(self, **user_data):
        """Create student using factory."""
        from .user_factory import create_student
        return create_student(self, **user_data)

    @transaction.atomic
    def create_teacher(self, create_profile=False, **user_data):
        """Create teacher using factory."""
        from .user_factory import create_teacher
        return create_teacher(self, create_profile=create_profile, **user_data)

    @transaction.atomic
    def create_staff(self, **user_data):
        """Create staff using factory."""
        from .user_factory import create_staff
        return create_staff(self, **user_data)


class SchoolUser(User):
    objects: SchoolUserManager = SchoolUserManager()
    schoolstaff: "SchoolStaff"
    student: "Student"
    parent: "Parent"

    class Meta:
        proxy = True
        verbose_name = "School User"

    @property
    def profile(self) -> ProfileClass | None:
        """Safely get user profile without fragile hasattr checks."""
        try:
            return self.parent
        except Parent.DoesNotExist:
            pass
        
        try:
            return self.student
        except Student.DoesNotExist:
            pass
        
        try:
            return self.schoolstaff
        except SchoolStaff.DoesNotExist:
            pass
        
        return None

    @property
    def is_parent(self) -> bool:
        """Check if user has Parent profile."""
        try:
            return self.parent is not None
        except Parent.DoesNotExist:
            return False

    @property
    def is_student(self) -> bool:
        """Check if user has Student profile."""
        try:
            return self.student is not None
        except Student.DoesNotExist:
            return False

    @property
    def is_school_staff(self) -> bool:
        """Check if user has SchoolStaff profile."""
        try:
            return self.schoolstaff is not None
        except SchoolStaff.DoesNotExist:
            return False

    @property
    def is_principal(self) -> bool:
        return self.groups.filter(name=RoleEnum.PRINCIPAL.value).exists() and self.is_school_staff
    
    @property
    def is_vp(self) -> bool:
        return self.groups.filter(name=RoleEnum.VP.value).exists() and self.is_school_staff

    @property
    def is_teacher(self) -> bool:
        return self.groups.filter(name=RoleEnum.TEACHER.value).exists() and self.is_school_staff

    @property
    def role(self) -> str | None:
        return self.groups.first().name if self.groups.exists() else None


class BaseUserTypeManager(models.Manager):
    """Manager with profile combination validation."""
    
    def _get_existing_profiles(self, user) -> set[ProfileType]:
        """Get all existing profile types for a user."""
        profiles = set()
        
        try:
            if user.parent:
                profiles.add(ProfileType.PARENT)
        except Parent.DoesNotExist:
            pass
        
        try:
            if user.student:
                profiles.add(ProfileType.STUDENT)
        except Student.DoesNotExist:
            pass
        
        try:
            if user.schoolstaff:
                profiles.add(ProfileType.SCHOOL_STAFF)
        except SchoolStaff.DoesNotExist:
            pass
        
        return profiles
    
    def _get_profile_type_for_model(self) -> ProfileType:
        """Get the ProfileType for this manager's model."""
        model_name = self.model.__name__
        
        type_map = {
            'Parent': ProfileType.PARENT,
            'Student': ProfileType.STUDENT,
            'SchoolStaff': ProfileType.SCHOOL_STAFF,
        }
        
        profile_type = type_map.get(model_name)
        if not profile_type:
            raise ValueError(f"Unknown profile model: {model_name}")
        
        return profile_type
    
    def create(self, user, **kwargs):
        """Create profile with validation based on allowed combinations."""
        # Get existing profiles
        existing_profiles = self._get_existing_profiles(user)
        
        # Get the profile type being created
        new_profile_type = self._get_profile_type_for_model()
        
        # Check if user already has this profile type
        if new_profile_type in existing_profiles:
            raise IntegrityError(
                f"User {user.get_full_name()} already has a {new_profile_type.value} profile"
            )
        
        # Calculate what the combination would be after creation
        proposed_profiles = existing_profiles | {new_profile_type}
        
        # Validate the combination is allowed
        if not validate_profile_combination(proposed_profiles):
            raise IntegrityError(
                f"Profile combination not allowed: {proposed_profiles}. "
                f"User already has: {existing_profiles}"
            )
        
        return super().create(user=user, **kwargs)


class BaseUserType(TimeStampedModel):
    """Base class for all user profile types with role-profile validation."""
    
    user = models.OneToOneField(
        SchoolUser, 
        on_delete=models.CASCADE,
        related_name="%(class)s"
    )
    address = models.TextField(blank=True, null=True)
    attributes = models.JSONField(
        blank=True, 
        null=True, 
        help_text="Additional attributes for the profile"
    )

    objects = BaseUserTypeManager()

    def __str__(self):
        return f"{self.__class__.__name__} profile of {self.user.get_full_name()}"
    
    def _get_profile_type(self) -> ProfileType:
        """Get the ProfileType for this profile instance."""
        model_name = self.__class__.__name__
        
        type_map = {
            'Parent': ProfileType.PARENT,
            'Student': ProfileType.STUDENT,
            'SchoolStaff': ProfileType.SCHOOL_STAFF,
        }
        
        profile_type = type_map.get(model_name)
        if not profile_type:
            raise ValueError(f"Unknown profile model: {model_name}")
        
        return profile_type
    
    def _get_user_roles(self) -> set[RoleEnum]:
        """Get all roles for this profile's user."""
        import contextlib
        
        role_names = self.user.groups.values_list('name', flat=True)
        roles = set()
        
        for role_name in role_names:
            with contextlib.suppress(ValueError):
                roles.add(RoleEnum(role_name))
        
        return roles
    
    def _get_user_profile_types(self) -> set[ProfileType]:
        """Get all profile types for this user."""
        profiles = set()
        
        try:
            if self.user.parent:
                profiles.add(ProfileType.PARENT)
        except Parent.DoesNotExist:
            pass
        
        try:
            if self.user.student:
                profiles.add(ProfileType.STUDENT)
        except Student.DoesNotExist:
            pass
        
        try:
            if self.user.schoolstaff:
                profiles.add(ProfileType.SCHOOL_STAFF)
        except SchoolStaff.DoesNotExist:
            pass
        
        return profiles
    
    def clean(self):
        """Validate role-profile consistency."""
        super().clean()
        
        # Only validate for existing instances
        if not self.pk:
            return
        
        # Get user's roles and profiles
        user_roles = self._get_user_roles()
        user_profiles = self._get_user_profile_types()
        
        # Validate consistency
        is_valid, error_msg = validate_role_profile_consistency(
            roles=user_roles,
            profile_types=user_profiles
        )
        
        if not is_valid:
            raise ValidationError({
                'user': f"Role-profile inconsistency: {error_msg}"
            })

    class Meta:
        abstract = True


class Parent(BaseUserType):
    childrens = models.ManyToManyField(SchoolUser, related_name="parents", blank=True)

    class Meta:
        verbose_name = "Parent "
        verbose_name_plural = "Parent s"
    
    def add_child(self, student):
        """Add a child to this parent with validation."""
        if not student.groups.filter(name=RoleEnum.STUDENT.value).exists():
            raise ValidationError(
                f"User {student.get_full_name()} must have STUDENT role to be added as a child."
            )
        self.childrens.add(student)
    
    def remove_child(self, student):
        """Remove a child from this parent."""
        self.childrens.remove(student)
    
    def get_children_list(self):
        """Get list of all children with STUDENT role validation."""
        return self.childrens.filter(groups__name=RoleEnum.STUDENT.value)
    
    def clean(self):
        """Validate that all children have STUDENT role."""
        super().clean()
        # Note: This validation only works for existing instances
        if self.pk:
            invalid_children = self.childrens.exclude(groups__name=RoleEnum.STUDENT.value)
            if invalid_children.exists():
                raise ValidationError({
                    'childrens': 'All children must have STUDENT role.'
                })


class Student(BaseUserType):
    class Meta:
        verbose_name = "Student "
        verbose_name_plural = "Student s"


class SchoolStaff(BaseUserType):
    class Meta:
        verbose_name = "School Staff"
        verbose_name_plural = "School Staff"
