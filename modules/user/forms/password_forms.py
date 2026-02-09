"""Password management forms."""

from django import forms
from django.contrib.auth.forms import (
    PasswordChangeForm,
    PasswordResetForm,
    SetPasswordForm,
)
from django.utils.translation import gettext_lazy as _

from modules.user.models import User


class CustomPasswordResetForm(PasswordResetForm):
    """Custom password reset form with styling."""

    email = forms.EmailField(
        label=_("Email"),
        max_length=254,
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": _("Enter your email address"),
                "autocomplete": "email",
            }
        ),
    )

    def get_users(self, email):
        """Return matching user(s) who should receive a reset."""
        active_users = User.objects.filter(email__iexact=email, is_active=True)
        return (
            user
            for user in active_users
            if user.has_usable_password() and user.email == email  # Exact match for security
        )


class CustomSetPasswordForm(SetPasswordForm):
    """Custom set password form with styling."""

    new_password1 = forms.CharField(
        label=_("New password"),
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": _("Enter new password"),
                "autocomplete": "new-password",
            }
        ),
        strip=False,
    )

    new_password2 = forms.CharField(
        label=_("New password confirmation"),
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": _("Confirm new password"),
                "autocomplete": "new-password",
            }
        ),
    )


class CustomPasswordChangeForm(PasswordChangeForm):
    """Custom password change form with styling."""

    old_password = forms.CharField(
        label=_("Old password"),
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": _("Enter current password"),
                "autocomplete": "current-password",
                "autofocus": True,
            }
        ),
    )

    new_password1 = forms.CharField(
        label=_("New password"),
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": _("Enter new password"),
                "autocomplete": "new-password",
            }
        ),
        strip=False,
    )

    new_password2 = forms.CharField(
        label=_("New password confirmation"),
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": _("Confirm new password"),
                "autocomplete": "new-password",
            }
        ),
    )
