"""Email verification forms."""

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from modules.user.models import User


class EmailVerificationForm(forms.Form):
    """Form for email verification."""

    email = forms.EmailField(
        label=_("Email Address"),
        help_text=_("Enter your email address to resend verification."),
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": _("Enter your email address"),
            }
        ),
    )

    def clean_email(self):
        """Validate that the email exists and is not already verified."""
        email = self.cleaned_data.get("email")
        try:
            user = User.objects.get(email=email)
            if user.is_verified:
                raise ValidationError(_("This email is already verified."))
        except User.DoesNotExist:
            raise ValidationError(_("No account found with this email address."))
        return email
