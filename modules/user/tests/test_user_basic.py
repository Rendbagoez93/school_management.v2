"""
Unit tests for User model - Basic functionality.

Tests:
- Basic user creation and field validation
- String representations
- Personal information fields
- Timestamp fields
"""

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


@pytest.mark.unit
@pytest.mark.user
@pytest.mark.django_db
class TestUserBasic:
    """Test cases for basic User model functionality."""

    def test_user_creation_with_factory(self, user_factory):
        """Test basic user creation using factory."""
        user = user_factory()

        # Check UUID primary key
        assert user.id is not None
        assert isinstance(str(user.id), str)

        # Check email
        assert user.email is not None
        assert "@" in user.email
        assert user.email == user.email.lower()  # Should be normalized

        # Check default status flags
        assert user.is_active is True
        assert user.is_staff is False
        assert user.is_superuser is False
        assert user.is_verified is False

        # Check timestamps
        assert user.date_joined is not None
        assert user.last_login is None  # No login yet

        # Check security defaults
        assert user.failed_login_attempts == 0
        assert user.account_locked_until is None

        # Check preferences defaults
        assert user.preferred_language == "en"
        assert user.timezone_preference == "UTC"
        assert user.email_notifications is True
        assert user.marketing_emails is False

    def test_user_string_representation(self, user_factory):
        """Test user string representation returns email."""
        user = user_factory(email="test@example.com")
        assert str(user) == "test@example.com"

    def test_user_repr(self, user_factory):
        """Test user detailed representation."""
        user = user_factory(email="test@example.com")
        repr_string = repr(user)
        assert "test@example.com" in repr_string
        assert "User" in repr_string
        assert repr_string == "<User: test@example.com>"

    def test_personal_information_fields(self, user_factory):
        """Test personal information fields are stored correctly."""
        from datetime import date

        user = user_factory(
            first_name="John",
            last_name="Doe",
            phone_number="+1234567890",
            date_of_birth=date(1990, 5, 15),
        )

        assert user.first_name == "John"
        assert user.last_name == "Doe"
        assert user.phone_number == "+1234567890"
        assert user.date_of_birth == date(1990, 5, 15)

    def test_timestamp_fields(self, user_factory):
        """Test timestamp fields behavior."""
        user = user_factory()

        # date_joined should be set automatically
        assert user.date_joined is not None
        assert isinstance(user.date_joined, timezone.datetime)

        # last_login starts as None
        assert user.last_login is None

        # email_verified_at starts as None for unverified users
        assert user.email_verified_at is None
        assert user.is_verified is False

    def test_clean_method_normalizes_email(self, user_factory):
        """Test that clean method normalizes email."""
        user = user_factory.build(email="Test@EXAMPLE.COM")
        user.clean()
        assert user.email == "test@example.com"
