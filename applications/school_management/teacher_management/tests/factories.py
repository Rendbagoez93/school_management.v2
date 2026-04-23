"""Factory definitions for teacher_management tests."""

import uuid
from datetime import date

import factory
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from config.roles import RoleEnum
from applications.school_management.teacher_management.models import Teacher

User = get_user_model()

_counter = 0


def _unique_email(prefix: str) -> str:
    global _counter
    _counter += 1
    return f"{prefix}_{_counter}_{uuid.uuid4().hex[:6]}@school.test"


class UserFactory(factory.django.DjangoModelFactory):
    """Minimal User without any group assignment."""

    class Meta:
        model = User

    email = factory.LazyFunction(lambda: _unique_email("user"))
    first_name = factory.Sequence(lambda n: f"First{n}")
    last_name = factory.Sequence(lambda n: f"Last{n}")
    password = factory.PostGenerationMethodCall("set_password", "TestPass123!")
    is_active = True


class TeacherUserFactory(UserFactory):
    """User with the Teacher role group attached."""

    @factory.post_generation
    def assign_group(self, create, extracted, **kwargs):
        if not create:
            return
        group, _ = Group.objects.get_or_create(name=RoleEnum.TEACHER.value)
        self.groups.add(group)
        self.role = RoleEnum.TEACHER.value
        self.save(update_fields=["role"])


class TeacherFactory(factory.django.DjangoModelFactory):
    """Creates a Teacher with a corresponding TeacherUserFactory user."""

    class Meta:
        model = Teacher

    user = factory.SubFactory(TeacherUserFactory)
    employee_id = factory.Sequence(lambda n: f"TCH{n:04d}")
    department = "Science"
    specialization = "Physics"
    date_of_joining = date(2022, 8, 1)
    is_active = True
