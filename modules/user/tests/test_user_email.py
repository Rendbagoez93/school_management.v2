"""
Unit tests for User model - Email functionality.

Tests:
- Email normalization
- Email uniqueness
- Email sending
"""

import pytest
from django.contrib.auth import get_user_model
from django.core import mail
from django.db import IntegrityError

User = get_user_model()


@pytest.mark.unit
@pytest.mark.user
@pytest.mark.django_db
class TestUserEmail:
    """Test cases for User model email functionality."""

    def test_email_normalization(self, user_factory):
        """Test email domain is normalized to lowercase."""
        user = user_factory(email="Test@EXAMPLE.COM")
        # Domain should be lowercase, local part unchanged
        assert user.email == "Test@example.com"

    def test_email_uniqueness(self, user_factory):
        """Test that emails must be unique."""
        user_factory(email="test@example.com")

        # Attempting to create user with same email should fail
        with pytest.raises(IntegrityError):
            user_factory(email="test@example.com")

    def test_email_case_insensitive_uniqueness(self, user_factory):
        """Test that email uniqueness is case-insensitive."""
        user_factory(email="test@example.com")

        # Different case should still be treated as duplicate
        with pytest.raises(IntegrityError):
            user_factory(email="TEST@EXAMPLE.COM")

    def test_email_user_method(self, user_factory):
        """Test sending email to user."""
        user = user_factory(email="test@example.com")

        # Send email
        subject = "Test Subject"
        message = "Test message content"
        user.email_user(subject, message)

        # Check that email was sent
        assert len(mail.outbox) == 1
        assert mail.outbox[0].subject == subject
        assert mail.outbox[0].body == message
        assert mail.outbox[0].to == ["test@example.com"]
