from typing import Union

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db import IntegrityError, models, transaction

from config.roles import RoleEnum
from modules.user.models import DefaultUserManager
from shared.base_models import TimeStampedModel

User = get_user_model()
ProfileClass = Union["Parent", "Student", "SchoolStaff"]


class SchoolUserManager(DefaultUserManager):
    def all(self):
        """Return all users in the school management system."""
        return self.filter(groups__name__in=RoleEnum.to_list()).prefetch_related("groups")

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

    # NOTE: Teacher profile creation moved to service layer to avoid duplication
    # Use teacher_management app's service layer for Teacher profile operations

    @transaction.atomic
    def create_principal(self, **user_data):
        group = Group.objects.get(name=RoleEnum.PRINCIPAL.value)
        user = self.create_staffuser(**user_data)
        SchoolStaff.objects.create(user=user)
        group.user_set.add(user)
        return user

    @transaction.atomic
    def create_vp(self, **user_data):
        group = Group.objects.get(name=RoleEnum.VP.value)
        user = self.create_staffuser(**user_data)
        SchoolStaff.objects.create(user=user)
        group.user_set.add(user)
        return user

    @transaction.atomic
    def create_parent(self, **user_data):
        group = Group.objects.get(name=RoleEnum.PARENT.value)
        user = self.create_user(**user_data)
        Parent.objects.create(user=user)
        group.user_set.add(user)
        return user

    @transaction.atomic
    def create_student(self, **user_data):
        group = Group.objects.get(name=RoleEnum.STUDENT.value)
        user = self.create_user(**user_data)
        Student.objects.create(user=user)
        group.user_set.add(user)
        return user

    @transaction.atomic
    def create_teacher(self, **user_data):
        """Create a teacher user with SchoolStaff profile.
        
        NOTE: Use teacher_management service layer to create Teacher profile
        for timetable/assignment functionality if needed.
        """

        group = Group.objects.get(name=RoleEnum.TEACHER.value)
        user = self.create_staffuser(**user_data)

        SchoolStaff.objects.create(user=user)
        group.user_set.add(user)
        
        return user

    @transaction.atomic
    def create_staff(self, **user_data):
        group = Group.objects.get(name=RoleEnum.STAFF.value)
        user = self.create_staffuser(**user_data)
        SchoolStaff.objects.create(user=user)
        group.user_set.add(user)
        return user


class SchoolUser(User):
    objects: SchoolUserManager = SchoolUserManager()
    schoolstaff: "SchoolStaff"
    student: "Student"
    parent: "Parent"

    class Meta:
        proxy = True
        verbose_name = "School User"

    @property
    def profile(self) -> ProfileClass:
        """Return the user's profile (Parent, Student, or SchoolStaff).
        
        NOTE: Profile access is kept for backward compatibility.
        Consider using direct access (user.parent, user.student, user.schoolstaff) instead.
        """
        if hasattr(self, "parent") and self.parent:
            return self.parent
        elif hasattr(self, "student") and self.student:
            return self.student
        elif hasattr(self, "schoolstaff") and self.schoolstaff:
            return self.schoolstaff
        raise ValueError("User profile not found.")

class BaseUserTypeManager(models.Manager):
    def create(self, user, **kwargs):
        """Create profile with validation that user has no existing profiles."""
        # Check if user already has any profile
        if hasattr(user, "parent") and user.parent:
            raise IntegrityError(f"User {user} already has a Parent profile")
        if hasattr(user, "student") and user.student:
            raise IntegrityError(f"User {user} already has a Student profile")
        if hasattr(user, "schoolstaff") and user.schoolstaff:
            raise IntegrityError(f"User {user} already has a SchoolStaff profile")

        return super().create(user=user, **kwargs)


class BaseUserType(TimeStampedModel):
    """Base model for user profiles with one-profile-per-user constraint.
    
    DB-level uniqueness is enforced by OneToOneField.
    Application-level validation in BaseUserTypeManager ensures no duplicate profiles.
    """
    user = models.OneToOneField(
        SchoolUser, 
        on_delete=models.CASCADE,
        related_name="%(class)s",
        help_text="One-to-one relationship ensures each user has only one profile of this type"
    )
    address = models.TextField(blank=True, null=True)
    attributes = models.JSONField(
        blank=True, 
        null=True, 
        help_text="Additional attributes for the profile (stored as JSON)"
    )

    objects = BaseUserTypeManager()

    def __str__(self):
        return f"Profile of {self.user.get_full_name()}"

    class Meta:
        abstract = True
        # NOTE: Concrete models may add additional constraints
        # Example: indexes = [models.Index(fields=['user', 'created_at'])]


class Parent(BaseUserType):
    children = models.ManyToManyField(
        SchoolUser, 
        related_name="parents", 
        blank=True,
        help_text="Students associated with this parent"
    )

    class Meta:
        verbose_name = "Parent"
        verbose_name_plural = "Parents"
    
    def add_child(self, student):
        """Add a child to this parent.
        
        NOTE: Role validation should be done in service layer before calling this method.
        """
        self.children.add(student)
    
    def remove_child(self, student):
        """Remove a child from this parent."""
        self.children.remove(student)
    
    def get_children_list(self):
        """Get list of all children.
        
        NOTE: Role filtering moved to service layer.
        This returns all associated children.
        """
        return self.children.all()
    
    def clean(self):
        """Validate parent profile.
        
        NOTE: Role validation has been moved to service layer.
        """
        super().clean()


class Student(BaseUserType):
    class Meta:
        verbose_name = "Student"
        verbose_name_plural = "Students"


class SchoolStaff(BaseUserType):
    class Meta:
        verbose_name = "School Staff"
        verbose_name_plural = "School Staff"
