"""
Unit tests for User model - Demographics functionality.

Tests:
- Age calculation
- Birthday checking
"""

from datetime import date, timedelta

import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.unit
@pytest.mark.user
@pytest.mark.django_db
class TestUserDemographics:
    """Test cases for User model demographics functionality."""

    def test_age_calculation(self, user_factory):
        """Test age calculation from date of birth."""
        # User born exactly 25 years ago today
        birth_date = date.today() - timedelta(days=25 * 365 + 6)  # Include leap years
        user = user_factory(date_of_birth=birth_date)

        age = user.get_age()
        assert age == 25

        # User born 30 years and 6 months ago
        birth_date_30 = date.today() - timedelta(days=30 * 365 + 183)
        user_30 = user_factory(date_of_birth=birth_date_30)
        assert user_30.get_age() == 30

        # User with no birth date
        user_no_birth = user_factory(date_of_birth=None)
        assert user_no_birth.get_age() is None

    def test_age_calculation_before_birthday(self, user_factory):
        """Test age calculation before birthday this year."""
        today = date.today()
        # Birthday next month (not yet celebrated this year)
        birth_date = date(today.year - 25, today.month + 1 if today.month < 12 else 1, 15)
        user = user_factory(date_of_birth=birth_date)

        # Should be 24, not 25 yet
        assert user.get_age() == 24

    def test_birthday_check(self, user_factory):
        """Test birthday checking."""
        today = date.today()

        # User with birthday today
        user_birthday_today = user_factory(
            date_of_birth=date(today.year - 25, today.month, today.day)
        )
        assert user_birthday_today.is_birthday_today() is True

        # User with birthday yesterday
        yesterday = today - timedelta(days=1)
        user_birthday_yesterday = user_factory(
            date_of_birth=date(today.year - 25, yesterday.month, yesterday.day)
        )
        assert user_birthday_yesterday.is_birthday_today() is False

        # User with birthday tomorrow
        tomorrow = today + timedelta(days=1)
        user_birthday_tomorrow = user_factory(
            date_of_birth=date(today.year - 25, tomorrow.month, tomorrow.day)
        )
        assert user_birthday_tomorrow.is_birthday_today() is False

        # User with no birth date
        user_no_birth = user_factory(date_of_birth=None)
        assert user_no_birth.is_birthday_today() is False
