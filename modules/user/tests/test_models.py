"""
Unit tests for User model.

This module tests all functionality of the User model including:
- Basic user creation and field validation
- String representations
- Name handling methods (get_full_name, get_short_name, display_name, initials)
- Email normalization and uniqueness
- Password management
- Email verification
- Security features (account locking, failed login tracking)
- Age calculation and birthday checking
- User preferences
- Phone number validation
- User manager methods
"""

from datetime import date, timedelta

import pytest
from django.contrib.auth import get_user_model
from django.core import mail
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone

User = get_user_model()


@pytest.mark.unit
@pytest.mark.user
@pytest.mark.django_db
class TestUserModel:
    """Test cases for User model functionality."""

    def test_user_creation_with_factory(self, user_factory):
        """Test basic user creation using factory."""
        user = user_factory()

        # Check UUID primary key
        assert user.id is not None
        assert isinstance(str(user.id), str)

        # Check email
        assert user.email is not None
        assert "@" in user.email
        assert user.email == user.email.lower()  # Should be normalized

        # Check default status flags
        assert user.is_active is True
        assert user.is_staff is False
        assert user.is_superuser is False
        assert user.is_verified is False

        # Check timestamps
        assert user.date_joined is not None
        assert user.last_login is None  # No login yet

        # Check security defaults
        assert user.failed_login_attempts == 0
        assert user.account_locked_until is None

        # Check preferences defaults
        assert user.preferred_language == "en"
        assert user.timezone_preference == "UTC"
        assert user.email_notifications is True
        assert user.marketing_emails is False

    def test_user_string_representation(self, user_factory):
        """Test user string representation returns email."""
        user = user_factory(email="test@example.com")
        assert str(user) == "test@example.com"

    def test_user_repr(self, user_factory):
        """Test user detailed representation."""
        user = user_factory(email="test@example.com")
        repr_string = repr(user)
        assert "test@example.com" in repr_string
        assert "User" in repr_string
        assert repr_string == "<User: test@example.com>"

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

    def test_clean_method_normalizes_email(self, user_factory):
        """Test that clean method normalizes email."""
        user = user_factory.build(email="Test@EXAMPLE.COM")
        user.clean()
        assert user.email == "Test@example.com"

    def test_personal_information_fields(self, user_factory):
        """Test personal information fields are stored correctly."""
        user = user_factory(
            first_name="John",
            last_name="Doe",
            phone_number="+1234567890",
            date_of_birth=date(1990, 5, 15),
        )

        assert user.first_name == "John"
        assert user.last_name == "Doe"
        assert user.phone_number == "+1234567890"
        assert user.date_of_birth == date(1990, 5, 15)

    def test_timestamp_fields(self, user_factory):
        """Test timestamp fields behavior."""
        user = user_factory()

        # date_joined should be set automatically
        assert user.date_joined is not None
        assert isinstance(user.date_joined, timezone.datetime)

        # last_login starts as None
        assert user.last_login is None

        # email_verified_at starts as None for unverified users
        assert user.email_verified_at is None
        assert user.is_verified is False


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
