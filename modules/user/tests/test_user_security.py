"""
Unit tests for User model - Security functionality.

Tests:
- Account locking
- Account lock expiration
- Failed login attempts
- Failed login reset
"""

from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


@pytest.mark.unit
@pytest.mark.user
@pytest.mark.django_db
class TestUserSecurity:
    """Test cases for User model security functionality."""

    def test_account_locking(self, user_factory):
        """Test account locking functionality."""
        user = user_factory()

        # Initially not locked
        assert user.is_account_locked() is False
        assert user.account_locked_until is None

        # Lock account for 30 minutes
        user.lock_account(duration_minutes=30)
        user.refresh_from_db()

        assert user.is_account_locked() is True
        assert user.account_locked_until is not None
        assert user.account_locked_until > timezone.now()

        # Unlock account
        user.unlock_account()
        user.refresh_from_db()

        assert user.is_account_locked() is False
        assert user.account_locked_until is None
        assert user.failed_login_attempts == 0

    def test_account_lock_expiration(self, user_factory):
        """Test that account lock expires after duration."""
        user = user_factory()

        # Lock account with past expiration time
        past_time = timezone.now() - timedelta(minutes=5)
        user.account_locked_until = past_time
        user.save()

        # Should not be locked anymore
        assert user.is_account_locked() is False

    def test_failed_login_attempts(self, user_factory):
        """Test failed login attempt tracking."""
        user = user_factory()
        assert user.failed_login_attempts == 0

        # Increment failed attempts multiple times
        for i in range(4):
            user.increment_failed_login()
            user.refresh_from_db()
            assert user.failed_login_attempts == i + 1
            assert user.is_account_locked() is False

        # 5th attempt should lock the account
        user.increment_failed_login()
        user.refresh_from_db()
        assert user.failed_login_attempts == 5
        assert user.is_account_locked() is True

    def test_reset_failed_login(self, user_factory):
        """Test resetting failed login attempts."""
        user = user_factory()

        # Add failed attempts
        for _ in range(3):
            user.increment_failed_login()

        user.refresh_from_db()
        assert user.failed_login_attempts == 3

        # Reset should clear attempts
        user.reset_failed_login()
        user.refresh_from_db()
        assert user.failed_login_attempts == 0
