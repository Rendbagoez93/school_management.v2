"""User profile and contact forms."""

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .models import User


class UserProfileForm(forms.ModelForm):
    """Form for updating user profile information."""

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "phone_number",
            "date_of_birth",
            "preferred_language",
            "timezone_preference",
            "email_notifications",
            "marketing_emails",
        ]

        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "phone_number": forms.TextInput(attrs={"class": "form-control"}),
            "date_of_birth": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "preferred_language": forms.Select(attrs={"class": "form-select"}),
            "timezone_preference": forms.TextInput(attrs={"class": "form-control"}),
            "email_notifications": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "marketing_emails": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add help text to fields
        self.fields["phone_number"].help_text = _("Phone number in international format (e.g., +1234567890)")

        self.fields["email_notifications"].help_text = _("Receive notifications about important account updates")
        self.fields["marketing_emails"].help_text = _("Receive promotional emails and newsletters")

    def clean_phone_number(self):
        """Validate phone number format."""
        phone_number = self.cleaned_data.get("phone_number")
        if phone_number:
            # Basic validation for international format
            import re

            pattern = r"^\+?1?\d{9,15}$"
            if not re.match(pattern, phone_number):
                raise ValidationError(_("Enter a valid phone number in international format (e.g., +1234567890)"))
        return phone_number


class ContactForm(forms.Form):
    """Generic contact form."""

    name = forms.CharField(
        max_length=100,
        label=_("Full Name"),
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": _("Enter your full name"),
            }
        ),
    )

    email = forms.EmailField(
        label=_("Email Address"),
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": _("Enter your email address"),
            }
        ),
    )

    subject = forms.CharField(
        max_length=200,
        label=_("Subject"),
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": _("Enter message subject"),
            }
        ),
    )

    message = forms.CharField(
        label=_("Message"),
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 5,
                "placeholder": _("Enter your message"),
            }
        ),
    )

    def send_email(self):
        """Send the contact form email."""
        # This would typically integrate with your email service
        # For now, it's a placeholder for the email sending logic
        # Implementation would use self.cleaned_data
        pass
