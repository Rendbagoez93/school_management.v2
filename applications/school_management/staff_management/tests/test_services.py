"""
Tests for StaffMemberService business logic.

Scenarios:
- create: success, duplicate employee_id, user not found, user already has profile
- update: partial field updates
- set_active: activate/deactivate idempotence
- delete: soft delete
- list_staff: filtering by department, is_active, search
"""

import pytest
from django.core.exceptions import ValidationError

from applications.school_management.staff_management.models import StaffMember
from applications.school_management.staff_management.schemas import (
    StaffMemberCreateSchema,
    StaffMemberUpdateSchema,
)
from applications.school_management.staff_management.services import StaffMemberService

from .factories import StaffMemberFactory, StaffUserFactory, UserFactory


@pytest.mark.django_db
class TestStaffMemberServiceCreate:
    def test_create_success(self):
        user = StaffUserFactory()
        data = StaffMemberCreateSchema(
            user_id=str(user.pk),
            employee_id="SVC001",
            department="IT",
            job_title="Support",
        )
        member = StaffMemberService.create(data)

        assert member.pk is not None
        assert member.employee_id == "SVC001"
        assert member.user_id == user.pk

    def test_create_normalises_employee_id(self):
        user = StaffUserFactory()
        data = StaffMemberCreateSchema(
            user_id=str(user.pk),
            employee_id="  svc002  ",
        )
        member = StaffMemberService.create(data)
        assert member.employee_id == "SVC002"

    def test_create_user_not_found_raises(self):
        import uuid
        data = StaffMemberCreateSchema(
            user_id=str(uuid.uuid4()),
            employee_id="SVC999",
        )
        with pytest.raises(ValidationError) as exc:
            StaffMemberService.create(data)
        assert "user_id" in exc.value.message_dict

    def test_create_duplicate_employee_id_raises(self):
        existing = StaffMemberFactory(employee_id="SVC003")
        user2 = StaffUserFactory()
        data = StaffMemberCreateSchema(
            user_id=str(user2.pk),
            employee_id="SVC003",
        )
        with pytest.raises(ValidationError) as exc:
            StaffMemberService.create(data)
        assert "employee_id" in exc.value.message_dict

    def test_create_user_already_has_profile_raises(self):
        member = StaffMemberFactory()
        data = StaffMemberCreateSchema(
            user_id=str(member.user_id),
            employee_id="SVC004",
        )
        with pytest.raises(ValidationError) as exc:
            StaffMemberService.create(data)
        assert "user_id" in exc.value.message_dict


@pytest.mark.django_db
class TestStaffMemberServiceUpdate:
    def test_update_department(self):
        member = StaffMemberFactory(department="Old Dept")
        data = StaffMemberUpdateSchema(department="New Dept")
        updated = StaffMemberService.update(member, data)
        assert updated.department == "New Dept"

    def test_update_job_title(self):
        member = StaffMemberFactory(job_title="Old Title")
        data = StaffMemberUpdateSchema(job_title="New Title")
        updated = StaffMemberService.update(member, data)
        assert updated.job_title == "New Title"

    def test_update_none_fields_not_overwritten(self):
        member = StaffMemberFactory(department="Keep This", job_title="Keep This Too")
        data = StaffMemberUpdateSchema()  # all None
        updated = StaffMemberService.update(member, data)
        assert updated.department == "Keep This"
        assert updated.job_title == "Keep This Too"


@pytest.mark.django_db
class TestStaffMemberServiceActivation:
    def test_deactivate(self):
        member = StaffMemberFactory(is_active=True)
        updated = StaffMemberService.set_active(member, is_active=False)
        assert updated.is_active is False

    def test_activate(self):
        member = StaffMemberFactory(is_active=False)
        updated = StaffMemberService.set_active(member, is_active=True)
        assert updated.is_active is True

    def test_idempotent_activation(self):
        member = StaffMemberFactory(is_active=True)
        original_modified = member.date_modified
        updated = StaffMemberService.set_active(member, is_active=True)
        assert updated.date_modified == original_modified


@pytest.mark.django_db
class TestStaffMemberServiceDelete:
    def test_soft_delete(self):
        member = StaffMemberFactory()
        pk = member.pk
        StaffMemberService.delete(member)
        assert not StaffMember.objects.filter(pk=pk).exists()
        assert StaffMember.all_objects.filter(pk=pk, is_deleted=True).exists()


@pytest.mark.django_db
class TestStaffMemberServiceList:
    def test_filter_by_department(self):
        StaffMemberFactory(department="Finance")
        StaffMemberFactory(department="IT")

        results = list(StaffMemberService.list_staff(department="Finance"))
        assert all(m.department == "Finance" for m in results)
        assert len(results) >= 1

    def test_filter_active_only(self):
        StaffMemberFactory(is_active=True)
        StaffMemberFactory(is_active=False)

        active = list(StaffMemberService.list_staff(is_active=True))
        assert all(m.is_active for m in active)

    def test_search_by_first_name(self):
        user = StaffUserFactory()
        user.first_name = "Zephyrine"
        user.save(update_fields=["first_name"])
        member = StaffMemberFactory(user=user)

        results = list(StaffMemberService.list_staff(search="Zephyrine"))
        assert any(m.pk == member.pk for m in results)

    def test_deleted_not_in_list(self):
        member = StaffMemberFactory()
        member.delete()

        results = list(StaffMemberService.list_staff())
        assert all(m.pk != member.pk for m in results)
