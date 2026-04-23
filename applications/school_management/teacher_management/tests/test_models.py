"""
Tests for Teacher model validation and constraints.

Scenarios covered:
- Valid teacher creation
- Employee ID normalization (uppercase, trimmed)
- Duplicate employee_id is rejected
- Non-teacher account cannot get a teacher profile
- Student account cannot become teacher
- Soft-delete and restore lifecycle
- Active manager excludes inactive and deleted records
"""

import pytest
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError

from config.roles import RoleEnum
from applications.school_management.teacher_management.models import Teacher

from .factories import TeacherFactory, TeacherUserFactory, UserFactory


@pytest.mark.django_db
class TestTeacherCreation:
    def test_creates_valid_teacher(self):
        teacher = TeacherFactory()
        assert teacher.pk is not None
        assert teacher.is_active is True
        assert teacher.is_deleted is False

    def test_employee_id_normalised_to_uppercase(self):
        user = TeacherUserFactory()
        teacher = Teacher(user=user, employee_id="  tch0099  ")
        teacher.save()
        assert teacher.employee_id == "TCH0099"

    def test_str_representation(self):
        teacher = TeacherFactory(employee_id="TCH0001")
        full_name = teacher.user.get_full_name()
        assert "TCH0001" in str(teacher)
        assert full_name in str(teacher)


@pytest.mark.django_db
class TestTeacherConstraints:
    def test_duplicate_employee_id_raises_integrity_error(self):
        TeacherFactory(employee_id="TCH9999")
        with pytest.raises(IntegrityError):
            Teacher.objects.create(
                user=TeacherUserFactory(),
                employee_id="TCH9999",
            )

    def test_user_without_teacher_role_is_rejected(self, db):
        user = UserFactory()  # no group
        with pytest.raises(ValidationError) as exc:
            t = Teacher(user=user, employee_id="TCH1111")
            t.save()
        assert "user" in exc.value.message_dict

    def test_student_cannot_be_teacher(self, db):
        student_group, _ = Group.objects.get_or_create(name=RoleEnum.STUDENT.value)
        user = UserFactory()
        user.groups.add(student_group)
        with pytest.raises(ValidationError) as exc:
            t = Teacher(user=user, employee_id="TCH2222")
            t.save()
        assert "user" in exc.value.message_dict

    def test_blank_employee_id_raises_validation_error(self):
        user = TeacherUserFactory()
        with pytest.raises(ValidationError) as exc:
            t = Teacher(user=user, employee_id="   ")
            t.save()
        assert "employee_id" in exc.value.message_dict


@pytest.mark.django_db
class TestTeacherSoftDelete:
    def test_soft_delete_sets_is_deleted(self):
        teacher = TeacherFactory()
        pk = teacher.pk
        teacher.delete()

        assert not Teacher.objects.filter(pk=pk).exists()
        deleted = Teacher.all_objects.get(pk=pk)
        assert deleted.is_deleted is True
        assert deleted.deleted_at is not None

    def test_restore_after_soft_delete(self):
        teacher = TeacherFactory()
        pk = teacher.pk
        teacher.delete()

        deleted = Teacher.all_objects.get(pk=pk)
        deleted.restore()

        restored = Teacher.objects.get(pk=pk)
        assert restored.is_deleted is False
        assert restored.deleted_at is None


@pytest.mark.django_db
class TestActiveTeacherManager:
    def test_excludes_inactive(self):
        active = TeacherFactory(is_active=True)
        inactive = TeacherFactory(is_active=False)

        pks = list(Teacher.active.values_list("pk", flat=True))
        assert active.pk in pks
        assert inactive.pk not in pks

    def test_excludes_deleted(self):
        teacher = TeacherFactory(is_active=True)
        teacher.delete()

        pks = list(Teacher.active.values_list("pk", flat=True))
        assert teacher.pk not in pks
