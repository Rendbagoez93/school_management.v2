"""
Unit tests for User model - Phone number functionality.

Tests:
- Phone number field validation
- Phone number format validation
"""

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()


@pytest.mark.unit
@pytest.mark.user
@pytest.mark.django_db
class TestUserPhone:
    """Test cases for User model phone number functionality."""

    def test_phone_number_field(self, user_factory):
        """Test phone number field with valid formats."""
        # Valid international format
        user = user_factory(phone_number="+1234567890")
        user.full_clean()  # Should not raise

        # Valid format without plus
        user2 = user_factory(phone_number="1234567890")
        user2.full_clean()  # Should not raise

    def test_phone_number_validation(self, user_factory):
        """Test phone number validation rejects invalid formats."""
        # Invalid: too short
        user = user_factory.build(phone_number="123")
        with pytest.raises(ValidationError):
            user.full_clean()

        # Invalid: contains letters
        user2 = user_factory.build(phone_number="1234abc5678")
        with pytest.raises(ValidationError):
            user2.full_clean()
