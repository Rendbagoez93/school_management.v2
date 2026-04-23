"""Factory definitions for staff_management tests.

Use these factories in tests instead of manual model.objects.create() calls.
"""

import uuid
from datetime import date

import factory
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from config.roles import RoleEnum
from applications.school_management.staff_management.models import StaffMember

User = get_user_model()

_counter = 0


def _unique_email(prefix: str) -> str:
    global _counter
    _counter += 1
    return f"{prefix}_{_counter}_{uuid.uuid4().hex[:6]}@school.test"


class UserFactory(factory.django.DjangoModelFactory):
    """Minimal User for staff tests. Not added to any group by default."""

    class Meta:
        model = User

    email = factory.LazyFunction(lambda: _unique_email("user"))
    first_name = factory.Sequence(lambda n: f"First{n}")
    last_name = factory.Sequence(lambda n: f"Last{n}")
    password = factory.PostGenerationMethodCall("set_password", "TestPass123!")
    is_active = True


class StaffUserFactory(UserFactory):
    """User with the Staff role group attached."""

    @factory.post_generation
    def assign_group(self, create, extracted, **kwargs):
        if not create:
            return
        group, _ = Group.objects.get_or_create(name=RoleEnum.STAFF.value)
        self.groups.add(group)
        self.role = RoleEnum.STAFF.value
        self.save(update_fields=["role"])


class StaffMemberFactory(factory.django.DjangoModelFactory):
    """Creates a StaffMember with a corresponding StaffUserFactory user."""

    class Meta:
        model = StaffMember

    user = factory.SubFactory(StaffUserFactory)
    employee_id = factory.Sequence(lambda n: f"STF{n:04d}")
    department = "Administration"
    job_title = "Clerk"
    date_of_joining = date(2023, 1, 15)
    is_active = True
