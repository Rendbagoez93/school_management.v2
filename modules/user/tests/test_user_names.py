"""
Unit tests for User model - Name handling functionality.

Tests:
- get_full_name method
- get_short_name method
- display_name property
- initials property
"""

import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.unit
@pytest.mark.user
@pytest.mark.django_db
class TestUserNames:
    """Test cases for User model name handling functionality."""

    def test_user_get_full_name(self, user_factory):
        """Test get_full_name method returns full name or email."""
        # Test with both names
        user = user_factory(first_name="John", last_name="Doe")
        assert user.get_full_name() == "John Doe"

        # Test with only first name
        user_first_only = user_factory(first_name="John", last_name="")
        assert user_first_only.get_full_name() == "John"

        # Test with only last name
        user_last_only = user_factory(first_name="", last_name="Doe")
        assert user_last_only.get_full_name() == "Doe"

        # Test with no names - should return email
        user_no_names = user_factory(first_name="", last_name="")
        assert user_no_names.get_full_name() == user_no_names.email

    def test_user_get_short_name(self, user_factory):
        """Test get_short_name returns first name or email prefix."""
        # Test with first name
        user = user_factory(first_name="John", email="john@example.com")
        assert user.get_short_name() == "John"

        # Test with no first name - should return email prefix
        user_no_first = user_factory(first_name="", email="johnbig@example.com")
        assert user_no_first.get_short_name() == "johnbig"

    def test_user_display_name_property(self, user_factory):
        """Test display_name property uses get_full_name."""
        user = user_factory(first_name="John", last_name="Doe")
        assert user.display_name == "John Doe"
        assert user.display_name == user.get_full_name()

    def test_user_initials_property(self, user_factory):
        """Test initials property generates correct initials."""
        # Test with both names
        user = user_factory(first_name="John", last_name="Doe")
        assert user.initials == "JD"

        # Test with only first name
        user_first_only = user_factory(first_name="John", last_name="")
        assert user_first_only.initials == "J"

        # Test with no names - should use first letter of email
        user_no_names = user_factory(first_name="", last_name="", email="jane@example.com")
        assert user_no_names.initials == "J"
