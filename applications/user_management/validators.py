from pydantic import BaseModel, EmailStr, Field, ValidationError

from applications.user_management.models import SchoolUser


class PrincipalSetupForm(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str
    confirm_password: str
    phone_number: str | None = Field(
        default=None,
        description="Optional phone number for the principal",
        validation_alias="phone",
    )

    def validate(self):
        """Validate the form data."""
        if self.password != self.confirm_password:
            raise ValidationError("Passwords do not match.")
        if SchoolUser.objects.get_principals().exists():
            raise ValidationError("Principal account has already been created.")
