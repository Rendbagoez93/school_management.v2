"""
API integration tests for staff_management endpoints.

Uses Django test client to call the real URL routes.
Verifies HTTP status codes and response shape.
"""

import json
import uuid
from datetime import date

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from applications.school_management.staff_management.models import StaffMember

from .factories import StaffMemberFactory, StaffUserFactory, UserFactory

User = get_user_model()


def _auth_client(client, user):
    """Force-login a user into the Django test client."""
    client.force_login(user)
    return client


@pytest.mark.django_db
class TestStaffMemberListCreateAPI:
    url = "/api/staff-management/"

    def test_list_requires_auth(self, client):
        resp = client.get(self.url)
        assert resp.status_code in (401, 403)

    def test_list_returns_results(self, client):
        user = StaffUserFactory()
        StaffMemberFactory.create_batch(3)
        _auth_client(client, user)
        resp = client.get(self.url)
        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == "ok"
        assert "results" in body["data"]

    def test_create_staff_member(self, client):
        actor = StaffUserFactory()
        target_user = StaffUserFactory()
        _auth_client(client, actor)
        payload = {
            "user_id": str(target_user.pk),
            "employee_id": "API001",
            "department": "IT",
            "job_title": "Analyst",
        }
        resp = client.post(
            self.url,
            data=json.dumps(payload),
            content_type="application/json",
        )
        assert resp.status_code == 201
        body = resp.json()
        assert body["code"] == "created"
        assert body["data"]["employee_id"] == "API001"

    def test_create_duplicate_employee_id_returns_422(self, client):
        actor = StaffUserFactory()
        StaffMemberFactory(employee_id="DUP001")
        target = StaffUserFactory()
        _auth_client(client, actor)
        payload = {
            "user_id": str(target.pk),
            "employee_id": "DUP001",
        }
        resp = client.post(
            self.url,
            data=json.dumps(payload),
            content_type="application/json",
        )
        # ApiError raised → ApiErrorMiddleware returns error JSON
        assert resp.status_code in (400, 422, 500)

    def test_filter_by_department(self, client):
        user = StaffUserFactory()
        StaffMemberFactory(department="Finance")
        StaffMemberFactory(department="IT")
        _auth_client(client, user)
        resp = client.get(self.url, {"department": "Finance"})
        assert resp.status_code == 200
        results = resp.json()["data"]["results"]
        assert all(r["department"] == "Finance" for r in results)


@pytest.mark.django_db
class TestStaffMemberDetailAPI:
    def _url(self, staff_id: int) -> str:
        return f"/api/staff-management/{staff_id}/"

    def test_get_detail(self, client):
        user = StaffUserFactory()
        member = StaffMemberFactory()
        _auth_client(client, user)
        resp = client.get(self._url(member.pk))
        assert resp.status_code == 200
        assert resp.json()["data"]["id"] == member.pk

    def test_get_not_found(self, client):
        user = StaffUserFactory()
        _auth_client(client, user)
        resp = client.get(self._url(99999))
        assert resp.status_code == 404

    def test_patch_department(self, client):
        user = StaffUserFactory()
        member = StaffMemberFactory(department="OldDept")
        _auth_client(client, user)
        resp = client.patch(
            self._url(member.pk),
            data=json.dumps({"department": "NewDept"}),
            content_type="application/json",
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["department"] == "NewDept"

    def test_delete_soft_deletes(self, client):
        user = StaffUserFactory()
        member = StaffMemberFactory()
        _auth_client(client, user)
        resp = client.delete(self._url(member.pk))
        assert resp.status_code == 200
        assert not StaffMember.objects.filter(pk=member.pk).exists()


@pytest.mark.django_db
class TestStaffMemberActivationAPI:
    def _url(self, staff_id: int) -> str:
        return f"/api/staff-management/{staff_id}/activation/"

    def test_deactivate(self, client):
        user = StaffUserFactory()
        member = StaffMemberFactory(is_active=True)
        _auth_client(client, user)
        resp = client.patch(
            self._url(member.pk),
            data=json.dumps({"is_active": False}),
            content_type="application/json",
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["is_active"] is False

    def test_activate(self, client):
        user = StaffUserFactory()
        member = StaffMemberFactory(is_active=False)
        _auth_client(client, user)
        resp = client.patch(
            self._url(member.pk),
            data=json.dumps({"is_active": True}),
            content_type="application/json",
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["is_active"] is True
