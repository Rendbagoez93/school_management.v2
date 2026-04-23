"""
Tests for TeacherService business logic.

Scenarios:
- create: success, missing teacher role, user not found, duplicate employee_id,
          user already has profile
- update: partial field updates, no-op on all-None input
- set_active: activate/deactivate, idempotence
- delete: soft delete
- list_teachers: filtering by department, specialization, is_active, search
"""

import uuid

import pytest
from django.core.exceptions import ValidationError

from applications.school_management.teacher_management.models import Teacher
from applications.school_management.teacher_management.schemas import (
    TeacherCreateSchema,
    TeacherUpdateSchema,
)
from applications.school_management.teacher_management.services import TeacherService

from .factories import TeacherFactory, TeacherUserFactory, UserFactory


@pytest.mark.django_db
class TestTeacherServiceCreate:
    def test_create_success(self):
        user = TeacherUserFactory()
        data = TeacherCreateSchema(
            user_id=str(user.pk),
            employee_id="SVC001",
            department="Maths",
            specialization="Algebra",
        )
        teacher = TeacherService.create(data)
        assert teacher.pk is not None
        assert teacher.employee_id == "SVC001"
        assert teacher.user_id == user.pk

    def test_create_normalises_employee_id(self):
        user = TeacherUserFactory()
        data = TeacherCreateSchema(user_id=str(user.pk), employee_id="  svc002  ")
        teacher = TeacherService.create(data)
        assert teacher.employee_id == "SVC002"

    def test_create_user_not_found_raises(self):
        data = TeacherCreateSchema(user_id=str(uuid.uuid4()), employee_id="SVC999")
        with pytest.raises(ValidationError) as exc:
            TeacherService.create(data)
        assert "user_id" in exc.value.message_dict

    def test_create_missing_teacher_role_raises(self):
        user = UserFactory()  # no role group
        data = TeacherCreateSchema(user_id=str(user.pk), employee_id="SVC003")
        with pytest.raises(ValidationError) as exc:
            TeacherService.create(data)
        assert "user_id" in exc.value.message_dict

    def test_create_duplicate_employee_id_raises(self):
        TeacherFactory(employee_id="SVC004")
        user2 = TeacherUserFactory()
        data = TeacherCreateSchema(user_id=str(user2.pk), employee_id="SVC004")
        with pytest.raises(ValidationError) as exc:
            TeacherService.create(data)
        assert "employee_id" in exc.value.message_dict

    def test_create_user_already_has_profile_raises(self):
        teacher = TeacherFactory()
        data = TeacherCreateSchema(user_id=str(teacher.user_id), employee_id="SVC005")
        with pytest.raises(ValidationError) as exc:
            TeacherService.create(data)
        assert "user_id" in exc.value.message_dict


@pytest.mark.django_db
class TestTeacherServiceUpdate:
    def test_update_department(self):
        teacher = TeacherFactory(department="Old Dept")
        data = TeacherUpdateSchema(department="New Dept")
        updated = TeacherService.update(teacher, data)
        assert updated.department == "New Dept"

    def test_update_specialization(self):
        teacher = TeacherFactory(specialization="Chemistry")
        data = TeacherUpdateSchema(specialization="Biology")
        updated = TeacherService.update(teacher, data)
        assert updated.specialization == "Biology"

    def test_update_none_fields_not_overwritten(self):
        teacher = TeacherFactory(department="Keep", specialization="Keep Too")
        data = TeacherUpdateSchema()  # all None
        updated = TeacherService.update(teacher, data)
        assert updated.department == "Keep"
        assert updated.specialization == "Keep Too"


@pytest.mark.django_db
class TestTeacherServiceActivation:
    def test_deactivate(self):
        teacher = TeacherFactory(is_active=True)
        updated = TeacherService.set_active(teacher, is_active=False)
        assert updated.is_active is False

    def test_activate(self):
        teacher = TeacherFactory(is_active=False)
        updated = TeacherService.set_active(teacher, is_active=True)
        assert updated.is_active is True

    def test_idempotent_activation(self):
        teacher = TeacherFactory(is_active=True)
        original_modified = teacher.date_modified
        updated = TeacherService.set_active(teacher, is_active=True)
        assert updated.date_modified == original_modified


@pytest.mark.django_db
class TestTeacherServiceDelete:
    def test_soft_delete(self):
        teacher = TeacherFactory()
        pk = teacher.pk
        TeacherService.delete(teacher)
        assert not Teacher.objects.filter(pk=pk).exists()
        assert Teacher.all_objects.filter(pk=pk, is_deleted=True).exists()


@pytest.mark.django_db
class TestTeacherServiceList:
    def test_filter_by_department(self):
        TeacherFactory(department="Science")
        TeacherFactory(department="Arts")
        results = list(TeacherService.list_teachers(department="Science"))
        assert all(t.department == "Science" for t in results)
        assert len(results) >= 1

    def test_filter_by_specialization_partial(self):
        TeacherFactory(specialization="Organic Chemistry")
        TeacherFactory(specialization="Physics")
        results = list(TeacherService.list_teachers(specialization="Chemistry"))
        assert all("Chemistry" in t.specialization for t in results)

    def test_filter_active_only(self):
        TeacherFactory(is_active=True)
        TeacherFactory(is_active=False)
        active = list(TeacherService.list_teachers(is_active=True))
        assert all(t.is_active for t in active)

    def test_search_by_first_name(self):
        user = TeacherUserFactory()
        user.first_name = "Bartholomew"
        user.save(update_fields=["first_name"])
        teacher = TeacherFactory(user=user)

        results = list(TeacherService.list_teachers(search="Bartholomew"))
        assert any(t.pk == teacher.pk for t in results)

    def test_deleted_not_in_list(self):
        teacher = TeacherFactory()
        teacher.delete()
        results = list(TeacherService.list_teachers())
        assert all(t.pk != teacher.pk for t in results)
