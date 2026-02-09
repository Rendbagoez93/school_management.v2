"""
Unit tests for User model - User Manager functionality.

Tests:
- create_user method
- create_superuser method
- create_staffuser method
- Email normalization in manager
- Error handling for invalid inputs
"""

import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.unit
@pytest.mark.user
@pytest.mark.django_db
class TestUserManager:
    """Test cases for User manager methods."""

    def test_create_user(self):
        """Test creating a regular user."""
        user = User.objects.create_user(
            email="test@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User",
        )

        assert user.email == "test@example.com"
        assert user.first_name == "Test"
        assert user.last_name == "User"
        assert user.is_active is True
        assert user.is_staff is False
        assert user.is_superuser is False
        assert user.check_password("testpass123")

    def test_create_user_without_password(self):
        """Test creating user without password."""
        user = User.objects.create_user(email="test@example.com")

        assert user.email == "test@example.com"
        assert user.is_active is True
        # Password should be unusable
        assert not user.has_usable_password()

    def test_create_superuser(self):
        """Test creating a superuser."""
        user = User.objects.create_superuser(email="admin@example.com", password="adminpass123")

        assert user.email == "admin@example.com"
        assert user.is_active is True
        assert user.is_staff is True
        assert user.is_superuser is True
        assert user.check_password("adminpass123")

    def test_create_staffuser(self):
        """Test creating a staff user."""
        user = User.objects.create_staffuser(email="staff@example.com", password="staffpass123")

        assert user.email == "staff@example.com"
        assert user.is_active is True
        assert user.is_staff is True
        assert user.is_superuser is False
        assert user.check_password("staffpass123")

    def test_create_user_without_email(self):
        """Test that creating user without email raises error."""
        with pytest.raises(ValueError, match="The Email field must be set"):
            User.objects.create_user(email="", password="testpass123")

        with pytest.raises(ValueError, match="The Email field must be set"):
            User.objects.create_user(email=None, password="testpass123")

    def test_create_superuser_without_staff_flag(self):
        """Test that creating superuser without is_staff=True raises error."""
        with pytest.raises(ValueError, match="Superuser must have is_staff=True"):
            User.objects.create_superuser(
                email="admin@example.com",
                password="adminpass123",
                is_staff=False,
            )

    def test_create_superuser_without_superuser_flag(self):
        """Test that creating superuser without is_superuser=True raises error."""
        with pytest.raises(ValueError, match="Superuser must have is_superuser=True"):
            User.objects.create_superuser(
                email="admin@example.com",
                password="adminpass123",
                is_superuser=False,
            )

    def test_create_staffuser_without_staff_flag(self):
        """Test that creating staff user without is_staff=True raises error."""
        with pytest.raises(ValueError, match="Staff user must have is_staff=True"):
            User.objects.create_staffuser(
                email="staff@example.com",
                password="staffpass123",
                is_staff=False,
            )

    def test_normalize_email(self):
        """Test email normalization in user creation."""
        user = User.objects.create_user(email="Test@EXAMPLE.COM", password="testpass123")

        # Domain should be lowercase
        assert user.email == "Test@example.com"
