"""
Unit tests for User model - Password functionality.

Tests:
- Password setting and verification
- Password hashing
"""

import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.unit
@pytest.mark.user
@pytest.mark.django_db
class TestUserPassword:
    """Test cases for User model password functionality."""

    def test_password_setting(self, user_factory):
        """Test password setting and verification."""
        user = user_factory()
        raw_password = "testpassword123"

        # Store original password_changed_at
        original_changed_at = user.password_changed_at

        user.set_password(raw_password)
        user.save()

        # Password should be hashed, not stored in plain text
        assert user.password != raw_password
        assert user.check_password(raw_password)
        assert not user.check_password("wrongpassword")

        # password_changed_at should be updated
        assert user.password_changed_at is not None
        if original_changed_at:
            assert user.password_changed_at > original_changed_at

    def test_password_hashing(self, user_factory):
        """Test that passwords are properly hashed."""
        password = "securepass123"
        user = user_factory(password=password)

        assert user.password.startswith("pbkdf2_sha256$") or user.password.startswith("bcrypt$")
        assert user.check_password(password)
