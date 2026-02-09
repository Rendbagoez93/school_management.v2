"""User manager classes for handling user creation and management."""

from typing import TYPE_CHECKING

from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _

if TYPE_CHECKING:
    from .models import AbstractUser


class DefaultUserManager(BaseUserManager):
    """
    Default user manager that handles user creation with email
    as the unique identifier.
    """

    def _create_user(self, email: str, password: str, **extra_fields) -> "AbstractUser":
        """Create and save a user with the given email and password."""
        if not email:
            raise ValueError(_("The Email field must be set"))

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email: str, password: str | None = None, **extra_fields) -> "AbstractUser":
        """Create and save a regular user with the given email and password."""
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        extra_fields.setdefault("is_active", True)
        return self._create_user(email, password, **extra_fields)

    def create_staffuser(self, email: str, password: str | None = None, **extra_fields) -> "AbstractUser":
        """Create and save a staff user with the given email and password."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", False)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Staff user must have is_staff=True."))

        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email: str, password: str, **extra_fields) -> "AbstractUser":
        """Create and save a superuser with the given email and password."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))

        return self._create_user(email, password, **extra_fields)
