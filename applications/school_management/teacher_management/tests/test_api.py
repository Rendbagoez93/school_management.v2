"""
API integration tests for teacher_management endpoints.

Uses Django test client to call the real URL routes.
Verifies HTTP status codes, response shapes, and edge cases.
"""

import json

import pytest
from django.contrib.auth import get_user_model

from applications.school_management.teacher_management.models import Teacher

from .factories import TeacherFactory, TeacherUserFactory, UserFactory

User = get_user_model()


def _auth_client(client, user):
    client.force_login(user)
    return client


@pytest.mark.django_db
class TestTeacherListCreateAPI:
    url = "/api/teachers/"

    def test_list_requires_auth(self, client):
        resp = client.get(self.url)
        assert resp.status_code in (401, 403)

    def test_list_returns_results(self, client):
        user = TeacherUserFactory()
        TeacherFactory.create_batch(3)
        _auth_client(client, user)
        resp = client.get(self.url)
        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == "ok"
        assert "results" in body["data"]

    def test_create_teacher_profile(self, client):
        actor = TeacherUserFactory()
        target = TeacherUserFactory()
        _auth_client(client, actor)
        payload = {
            "user_id": str(target.pk),
            "employee_id": "API001",
            "department": "Maths",
            "specialization": "Calculus",
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

    def test_create_non_teacher_user_rejected(self, client):
        actor = TeacherUserFactory()
        non_teacher = UserFactory()  # no Teacher group
        _auth_client(client, actor)
        payload = {"user_id": str(non_teacher.pk), "employee_id": "API002"}
        resp = client.post(
            self.url,
            data=json.dumps(payload),
            content_type="application/json",
        )
        assert resp.status_code in (400, 422, 500)

    def test_filter_by_department(self, client):
        user = TeacherUserFactory()
        TeacherFactory(department="Science")
        TeacherFactory(department="Arts")
        _auth_client(client, user)
        resp = client.get(self.url, {"department": "Science"})
        assert resp.status_code == 200
        results = resp.json()["data"]["results"]
        assert all(r["department"] == "Science" for r in results)


@pytest.mark.django_db
class TestTeacherDetailAPI:
    def _url(self, teacher_id: int) -> str:
        return f"/api/teachers/{teacher_id}/"

    def test_get_detail(self, client):
        user = TeacherUserFactory()
        teacher = TeacherFactory()
        _auth_client(client, user)
        resp = client.get(self._url(teacher.pk))
        assert resp.status_code == 200
        assert resp.json()["data"]["id"] == teacher.pk

    def test_get_not_found(self, client):
        user = TeacherUserFactory()
        _auth_client(client, user)
        resp = client.get(self._url(99999))
        assert resp.status_code == 404

    def test_patch_department(self, client):
        user = TeacherUserFactory()
        teacher = TeacherFactory(department="OldDept")
        _auth_client(client, user)
        resp = client.patch(
            self._url(teacher.pk),
            data=json.dumps({"department": "NewDept"}),
            content_type="application/json",
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["department"] == "NewDept"

    def test_delete_soft_deletes(self, client):
        user = TeacherUserFactory()
        teacher = TeacherFactory()
        _auth_client(client, user)
        resp = client.delete(self._url(teacher.pk))
        assert resp.status_code == 200
        assert not Teacher.objects.filter(pk=teacher.pk).exists()


@pytest.mark.django_db
class TestTeacherActivationAPI:
    def _url(self, teacher_id: int) -> str:
        return f"/api/teachers/{teacher_id}/activation/"

    def test_deactivate(self, client):
        user = TeacherUserFactory()
        teacher = TeacherFactory(is_active=True)
        _auth_client(client, user)
        resp = client.patch(
            self._url(teacher.pk),
            data=json.dumps({"is_active": False}),
            content_type="application/json",
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["is_active"] is False

    def test_activate(self, client):
        user = TeacherUserFactory()
        teacher = TeacherFactory(is_active=False)
        _auth_client(client, user)
        resp = client.patch(
            self._url(teacher.pk),
            data=json.dumps({"is_active": True}),
            content_type="application/json",
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["is_active"] is True
