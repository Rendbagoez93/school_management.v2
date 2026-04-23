"""
Tests for StaffMember model validation and constraints.

Scenarios covered:
- Valid staff member creation
- Employee ID normalization (uppercase, trimmed)
- Duplicate employee_id is rejected
- Student account cannot become staff
- Parent account cannot become staff
- Soft-delete and restore lifecycle
"""

import pytest
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError

from config.roles import RoleEnum
from applications.school_management.staff_management.models import StaffMember

from .factories import StaffMemberFactory, StaffUserFactory, UserFactory


@pytest.mark.django_db
class TestStaffMemberCreation:
    def test_creates_valid_staff_member(self):
        member = StaffMemberFactory()
        assert member.pk is not None
        assert member.is_active is True
        assert member.is_deleted is False

    def test_employee_id_normalised_to_uppercase(self):
        user = StaffUserFactory()
        member = StaffMember(
            user=user,
            employee_id="  stf0099  ",
            department="Finance",
        )
        member.save()
        assert member.employee_id == "STF0099"

    def test_str_representation(self):
        member = StaffMemberFactory(
            employee_id="STF0001",
        )
        full_name = member.user.get_full_name()
        assert "STF0001" in str(member)
        assert full_name in str(member)


@pytest.mark.django_db
class TestStaffMemberConstraints:
    def test_duplicate_employee_id_raises_integrity_error(self):
        member = StaffMemberFactory(employee_id="STF9999")
        with pytest.raises(IntegrityError):
            StaffMember.objects.create(
                user=StaffUserFactory(),
                employee_id="STF9999",
            )

    def test_student_account_cannot_be_staff(self, db):
        student_group, _ = Group.objects.get_or_create(name=RoleEnum.STUDENT.value)
        user = UserFactory()
        user.groups.add(student_group)

        with pytest.raises(ValidationError) as exc:
            member = StaffMember(user=user, employee_id="STF1111")
            member.save()

        assert "user" in exc.value.message_dict

    def test_parent_account_cannot_be_staff(self, db):
        parent_group, _ = Group.objects.get_or_create(name=RoleEnum.PARENT.value)
        user = UserFactory()
        user.groups.add(parent_group)

        with pytest.raises(ValidationError) as exc:
            member = StaffMember(user=user, employee_id="STF2222")
            member.save()

        assert "user" in exc.value.message_dict

    def test_blank_employee_id_raises_validation_error(self):
        user = StaffUserFactory()
        with pytest.raises(ValidationError) as exc:
            member = StaffMember(user=user, employee_id="   ")
            member.save()
        assert "employee_id" in exc.value.message_dict


@pytest.mark.django_db
class TestStaffMemberSoftDelete:
    def test_soft_delete_sets_is_deleted(self):
        member = StaffMemberFactory()
        pk = member.pk
        member.delete()

        # objects manager excludes deleted records
        assert not StaffMember.objects.filter(pk=pk).exists()
        # all_objects includes them
        deleted = StaffMember.all_objects.get(pk=pk)
        assert deleted.is_deleted is True
        assert deleted.deleted_at is not None

    def test_restore_after_soft_delete(self):
        member = StaffMemberFactory()
        pk = member.pk
        member.delete()

        deleted = StaffMember.all_objects.get(pk=pk)
        deleted.restore()

        restored = StaffMember.objects.get(pk=pk)
        assert restored.is_deleted is False
        assert restored.deleted_at is None


@pytest.mark.django_db
class TestActiveManager:
    def test_active_manager_excludes_inactive(self):
        active = StaffMemberFactory(is_active=True)
        inactive = StaffMemberFactory(is_active=False)

        pks = list(StaffMember.active.values_list("pk", flat=True))
        assert active.pk in pks
        assert inactive.pk not in pks

    def test_active_manager_excludes_deleted(self):
        member = StaffMemberFactory(is_active=True)
        member.delete()

        pks = list(StaffMember.active.values_list("pk", flat=True))
        assert member.pk not in pks
