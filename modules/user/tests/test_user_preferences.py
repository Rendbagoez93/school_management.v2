"""
Unit tests for User model - User preferences functionality.

Tests:
- User preferences fields
- User preferences defaults
"""

import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.unit
@pytest.mark.user
@pytest.mark.django_db
class TestUserPreferences:
    """Test cases for User model preferences functionality."""

    def test_user_preferences(self, user_factory):
        """Test user preferences fields."""
        user = user_factory(
            preferred_language="id",
            timezone_preference="Asia/Jakarta",
            email_notifications=False,
            marketing_emails=True,
        )

        assert user.preferred_language == "id"
        assert user.timezone_preference == "Asia/Jakarta"
        assert user.email_notifications is False
        assert user.marketing_emails is True

    def test_user_preferences_defaults(self, user_factory):
        """Test user preferences default values."""
        user = user_factory()

        assert user.preferred_language == "en"
        assert user.timezone_preference == "UTC"
        assert user.email_notifications is True
        assert user.marketing_emails is False
