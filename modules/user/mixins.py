"""Reusable model mixins for user-related functionality."""

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class TimestampMixin(models.Model):
    """Mixin for user-specific timestamp fields."""

    email_verified_at = models.DateTimeField(
        _("email verified at"),
        null=True,
        blank=True,
        help_text=_("The date and time when the email was verified."),
    )

    password_changed_at = models.DateTimeField(
        _("password changed at"),
        null=True,
        blank=True,
        help_text=_("The date and time when the password was last changed."),
    )

    class Meta:
        abstract = True


class SecurityMixin(models.Model):
    """Mixin for security-related fields and methods."""

    failed_login_attempts = models.PositiveIntegerField(
        _("failed login attempts"),
        default=0,
        help_text=_("Number of consecutive failed login attempts."),
    )

    account_locked_until = models.DateTimeField(
        _("account locked until"),
        null=True,
        blank=True,
        help_text=_("Account is locked until this date and time."),
    )

    class Meta:
        abstract = True

    def is_account_locked(self) -> bool:
        """Check if the account is currently locked."""
        if self.account_locked_until:
            return timezone.now() < self.account_locked_until
        return False

    def lock_account(self, duration_minutes: int = 30) -> None:
        """Lock the account for the specified duration."""
        self.account_locked_until = timezone.now() + timezone.timedelta(minutes=duration_minutes)
        self.save(update_fields=["account_locked_until"])

    def unlock_account(self) -> None:
        """Unlock the account and reset failed login attempts."""
        self.account_locked_until = None
        self.failed_login_attempts = 0
        self.save(update_fields=["account_locked_until", "failed_login_attempts"])

    def increment_failed_login(self) -> None:
        """
        Increment failed login attempts and lock account if threshold reached.
        """
        self.failed_login_attempts += 1
        if self.failed_login_attempts >= 5:  # Lock after 5 failed attempts
            self.lock_account()
        self.save(update_fields=["failed_login_attempts"])

    def reset_failed_login(self) -> None:
        """Reset failed login attempts counter."""
        self.failed_login_attempts = 0
        self.save(update_fields=["failed_login_attempts"])


class PreferencesMixin(models.Model):
    """Mixin for user preferences."""

    preferred_language = models.CharField(
        _("preferred language"),
        max_length=10,
        choices=[
            ("en", _("English")),
            ("id", _("Indonesian")),
        ],
        default="en",
        help_text=_("User's preferred language for the interface."),
    )

    timezone_preference = models.CharField(
        _("timezone"),
        max_length=50,
        default="UTC",
        help_text=_("User's preferred timezone."),
    )

    email_notifications = models.BooleanField(
        _("email notifications"),
        default=True,
        help_text=_("Receive email notifications for important updates."),
    )

    marketing_emails = models.BooleanField(
        _("marketing emails"),
        default=False,
        help_text=_("Receive marketing and promotional emails."),
    )

    class Meta:
        abstract = True
