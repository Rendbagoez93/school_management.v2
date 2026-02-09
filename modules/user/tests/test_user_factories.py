"""
Unit tests for User factories.

Tests:
- verified_user_factory
- staff_user_factory
- admin_user_factory
- inactive_user_factory
- locked_user_factory
- user_factory with password
- user_factory batch creation
- user_factory unique email generation
"""

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


@pytest.mark.unit
@pytest.mark.user
@pytest.mark.django_db
class TestUserFactories:
    """Test the user factories themselves."""

    def test_verified_user_factory(self, verified_user_factory):
        """Test verified user factory creates verified users."""
        user = verified_user_factory()
        assert user.is_verified is True
        assert user.email_verified_at is not None
        assert isinstance(user.email_verified_at, timezone.datetime)

    def test_staff_user_factory(self, staff_user_factory):
        """Test staff user factory creates staff users."""
        user = staff_user_factory()
        assert user.is_staff is True
        assert user.is_superuser is False
        assert user.is_verified is True
        assert user.email_verified_at is not None

    def test_admin_user_factory(self, admin_user_factory):
        """Test admin user factory creates superusers."""
        user = admin_user_factory()
        assert user.is_staff is True
        assert user.is_superuser is True
        assert user.is_verified is True
        assert user.email_verified_at is not None
        assert "admin" in user.email

    def test_inactive_user_factory(self, inactive_user_factory):
        """Test inactive user factory creates inactive users."""
        user = inactive_user_factory()
        assert user.is_active is False

    def test_locked_user_factory(self, locked_user_factory):
        """Test locked user factory creates locked users."""
        user = locked_user_factory()
        assert user.failed_login_attempts == 5
        assert user.account_locked_until is not None
        assert user.is_account_locked() is True

    def test_user_factory_with_password(self, user_factory):
        """Test user factory with custom password."""
        custom_password = "mycustompassword123"
        user = user_factory(password=custom_password)
        assert user.check_password(custom_password)

    def test_user_factory_batch_creation(self, user_factory):
        """Test creating multiple users with factory."""
        users = user_factory.create_batch(5)
        assert len(users) == 5

        # Check that all users have unique emails
        emails = [user.email for user in users]
        assert len(set(emails)) == 5  # All emails should be unique

    def test_user_factory_default_password(self, user_factory):
        """Test user factory sets default password."""
        user = user_factory()
        # Factory should set a default password
        assert user.has_usable_password()
        assert user.check_password("defaultpassword123")

    def test_user_factory_generates_unique_emails(self, user_factory):
        """Test that factory generates unique emails for each user."""
        user1 = user_factory()
        user2 = user_factory()
        user3 = user_factory()

        assert user1.email != user2.email
        assert user2.email != user3.email
        assert user1.email != user3.email
