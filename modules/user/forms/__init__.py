"""Forms package for user module."""

from .auth_forms import CustomAuthenticationForm
from .password_forms import (
    CustomPasswordChangeForm,
    CustomPasswordResetForm,
    CustomSetPasswordForm,
)
from .registration import CustomUserCreationForm
from .verification import EmailVerificationForm

__all__ = [
    "CustomUserCreationForm",
    "CustomAuthenticationForm",
    "CustomPasswordResetForm",
    "CustomSetPasswordForm",
    "CustomPasswordChangeForm",
    "EmailVerificationForm",
]
