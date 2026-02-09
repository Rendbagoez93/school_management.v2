"""
Pytest fixtures and factories for user module tests.
"""

from datetime import date, timedelta

import factory
import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from factory.django import DjangoModelFactory

User = get_user_model()


class UserFactory(DjangoModelFactory):
    """Factory for creating User instances for testing."""

    class Meta:
        model = User

    # User identification
    email = factory.Sequence(lambda n: f"user{n}@example.com")

    # Personal information
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    phone_number = factory.Faker("phone_number", locale="en_US")
    date_of_birth = factory.LazyFunction(lambda: date.today() - timedelta(days=25 * 365))

    # Account status
    is_active = True
    is_staff = False
    is_superuser = False
    is_verified = False

    # Security fields
    failed_login_attempts = 0
    account_locked_until = None

    # Preferences
    preferred_language = "en"
    timezone_preference = "UTC"
    email_notifications = True
    marketing_emails = False

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """Override create to normalize email before saving."""
        # Normalize email domain to lowercase
        email = kwargs.get('email', '')
        if email and '@' in email:
            local_part, domain = email.rsplit('@', 1)
            kwargs['email'] = f"{local_part}@{domain.lower()}"
        
        # Call the default create method
        return super()._create(model_class, *args, **kwargs)

    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        """Set password after instance creation."""
        if not create:
            return

        if extracted:
            self.set_password(extracted)
        else:
            self.set_password("defaultpassword123")


class VerifiedUserFactory(UserFactory):
    """Factory for creating verified users."""

    is_verified = True
    email_verified_at = factory.LazyFunction(timezone.now)


class StaffUserFactory(VerifiedUserFactory):
    """Factory for creating staff users."""

    is_staff = True
    email = factory.Sequence(lambda n: f"staff{n}@example.com")


class AdminUserFactory(VerifiedUserFactory):
    """Factory for creating admin/superuser users."""

    is_staff = True
    is_superuser = True
    email = factory.Sequence(lambda n: f"admin{n}@example.com")


class InactiveUserFactory(UserFactory):
    """Factory for creating inactive users."""

    is_active = False


class LockedUserFactory(UserFactory):
    """Factory for creating locked users."""

    failed_login_attempts = 5
    account_locked_until = factory.LazyFunction(lambda: timezone.now() + timedelta(minutes=30))


# Pytest fixtures
@pytest.fixture
def user_factory():
    """Fixture that returns the UserFactory class."""
    return UserFactory


@pytest.fixture
def verified_user_factory():
    """Fixture that returns the VerifiedUserFactory class."""
    return VerifiedUserFactory


@pytest.fixture
def staff_user_factory():
    """Fixture that returns the StaffUserFactory class."""
    return StaffUserFactory


@pytest.fixture
def admin_user_factory():
    """Fixture that returns the AdminUserFactory class."""
    return AdminUserFactory


@pytest.fixture
def inactive_user_factory():
    """Fixture that returns the InactiveUserFactory class."""
    return InactiveUserFactory


@pytest.fixture
def locked_user_factory():
    """Fixture that returns the LockedUserFactory class."""
    return LockedUserFactory
