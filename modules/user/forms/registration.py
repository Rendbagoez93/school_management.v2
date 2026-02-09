"""User registration forms."""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from modules.user.models import User


class CustomUserCreationForm(UserCreationForm):
    """Custom user creation form with additional fields."""

    email = forms.EmailField(
        required=True,
        help_text=_("Required. Enter a valid email address."),
        widget=forms.EmailInput(attrs={"class": "form-control"}),
    )

    first_name = forms.CharField(
        max_length=150,
        required=False,
        help_text=_("Optional. 150 characters or fewer."),
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

    last_name = forms.CharField(
        max_length=150,
        required=False,
        help_text=_("Optional. 150 characters or fewer."),
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

    phone_number = forms.CharField(
        max_length=17,
        required=False,
        help_text=_("Optional. Phone number in international format."),
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

    date_of_birth = forms.DateField(
        required=False,
        help_text=_("Optional. Your date of birth."),
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}),
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "date_of_birth",
            "password1",
            "password2",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add CSS classes to password fields
        self.fields["password1"].widget.attrs.update({"class": "form-control"})
        self.fields["password2"].widget.attrs.update({"class": "form-control"})

    def clean_email(self):
        """Validate that the email is unique."""
        email = self.cleaned_data.get("email")
        if email and User.objects.filter(email=email).exists():
            raise ValidationError(_("A user with this email address already exists."))
        return email

    def save(self, commit=True):
        """Save the user with the provided information."""
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.phone_number = self.cleaned_data["phone_number"]
        user.date_of_birth = self.cleaned_data["date_of_birth"]
        if commit:
            user.save()
        return user
