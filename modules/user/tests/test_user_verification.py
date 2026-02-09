"""
Unit tests for User model - Email verification functionality.

Tests:
- Email verification
"""

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


@pytest.mark.unit
@pytest.mark.user
@pytest.mark.django_db
class TestUserVerification:
    """Test cases for User model email verification functionality."""

    def test_email_verification(self, user_factory):
        """Test email verification functionality."""
        user = user_factory(is_verified=False)

        # Initially not verified
        assert user.is_verified is False
        assert user.email_verified_at is None

        # Verify email
        user.verify_email()

        # Should now be verified with timestamp
        assert user.is_verified is True
        assert user.email_verified_at is not None
        assert isinstance(user.email_verified_at, timezone.datetime)
