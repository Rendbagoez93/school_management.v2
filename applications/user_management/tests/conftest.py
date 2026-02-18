"""
Pytest fixtures for user_management app tests.

This module provides comprehensive fixtures for testing user profiles,
roles, and relationships in the school management system.
"""

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from config.roles import RoleEnum
from applications.user_management.models import Parent, SchoolStaff, SchoolUser, Student

User = get_user_model()


@pytest.fixture(scope="session")
def django_db_setup(django_db_setup, django_db_blocker):
    """Set up database with required groups for the session."""
    with django_db_blocker.unblock():
        # Create all role groups
        for role in RoleEnum:
            Group.objects.get_or_create(name=role.value)


@pytest.fixture
def base_user_data():
    """Provide base user data for creating users."""
    return {
        "first_name": "Test",
        "last_name": "User",
        "password": "TestPass123!",
    }


@pytest.fixture
def student_user_data(base_user_data):
    """Provide student user data."""
    return {
        **base_user_data,
        "email": "student@school.com",
        "first_name": "John",
        "last_name": "Student",
    }


@pytest.fixture
def parent_user_data(base_user_data):
    """Provide parent user data."""
    return {
        **base_user_data,
        "email": "parent@school.com",
        "first_name": "Jane",
        "last_name": "Parent",
    }


@pytest.fixture
def teacher_user_data(base_user_data):
    """Provide teacher user data."""
    return {
        **base_user_data,
        "email": "teacher@school.com",
        "first_name": "Mike",
        "last_name": "Teacher",
    }


@pytest.fixture
def staff_user_data(base_user_data):
    """Provide staff user data."""
    return {
        **base_user_data,
        "email": "staff@school.com",
        "first_name": "Anna",
        "last_name": "Staff",
    }


@pytest.fixture
def principal_user_data(base_user_data):
    """Provide principal user data."""
    return {
        **base_user_data,
        "email": "principal@school.com",
        "first_name": "Robert",
        "last_name": "Principal",
    }


@pytest.fixture
def vp_user_data(base_user_data):
    """Provide vice principal user data."""
    return {
        **base_user_data,
        "email": "vp@school.com",
        "first_name": "Sarah",
        "last_name": "VicePrincipal",
    }


# Role Group Fixtures
@pytest.fixture
def student_group(db):
    """Get or create STUDENT group."""
    group, _ = Group.objects.get_or_create(name=RoleEnum.STUDENT.value)
    return group


@pytest.fixture
def parent_group(db):
    """Get or create PARENT group."""
    group, _ = Group.objects.get_or_create(name=RoleEnum.PARENT.value)
    return group


@pytest.fixture
def teacher_group(db):
    """Get or create TEACHER group."""
    group, _ = Group.objects.get_or_create(name=RoleEnum.TEACHER.value)
    return group


@pytest.fixture
def staff_group(db):
    """Get or create STAFF group."""
    group, _ = Group.objects.get_or_create(name=RoleEnum.STAFF.value)
    return group


@pytest.fixture
def principal_group(db):
    """Get or create PRINCIPAL group."""
    group, _ = Group.objects.get_or_create(name=RoleEnum.PRINCIPAL.value)
    return group


@pytest.fixture
def vp_group(db):
    """Get or create VP group."""
    group, _ = Group.objects.get_or_create(name=RoleEnum.VP.value)
    return group


# User Creation Fixtures
@pytest.fixture
def create_student(db, student_group):
    """Factory fixture for creating student users."""
    def _create_student(email="student@test.com", **kwargs):
        user_data = {
            "email": email,
            "first_name": kwargs.get("first_name", "Test"),
            "last_name": kwargs.get("last_name", "Student"),
        }
        return SchoolUser.objects.create_student(**user_data)
    
    return _create_student


@pytest.fixture
def create_parent(db, parent_group):
    """Factory fixture for creating parent users."""
    def _create_parent(email="parent@test.com", **kwargs):
        user_data = {
            "email": email,
            "first_name": kwargs.get("first_name", "Test"),
            "last_name": kwargs.get("last_name", "Parent"),
        }
        return SchoolUser.objects.create_parent(**user_data)
    
    return _create_parent


@pytest.fixture
def create_teacher(db, teacher_group):
    """Factory fixture for creating teacher users."""
    def _create_teacher(email="teacher@test.com", **kwargs):
        user_data = {
            "email": email,
            "first_name": kwargs.get("first_name", "Test"),
            "last_name": kwargs.get("last_name", "Teacher"),
        }
        return SchoolUser.objects.create_teacher(**user_data)
    
    return _create_teacher


@pytest.fixture
def create_principal(db, principal_group):
    """Factory fixture for creating principal users."""
    def _create_principal(email="principal@test.com", **kwargs):
        user_data = {
            "email": email,
            "first_name": kwargs.get("first_name", "Test"),
            "last_name": kwargs.get("last_name", "Principal"),
        }
        return SchoolUser.objects.create_principal(**user_data)
    
    return _create_principal


@pytest.fixture
def create_vp(db, vp_group):
    """Factory fixture for creating vice principal users."""
    def _create_vp(email="vp@test.com", **kwargs):
        user_data = {
            "email": email,
            "first_name": kwargs.get("first_name", "Test"),
            "last_name": kwargs.get("last_name", "VP"),
        }
        return SchoolUser.objects.create_vp(**user_data)
    
    return _create_vp


@pytest.fixture
def create_staff(db, staff_group):
    """Factory fixture for creating staff users."""
    def _create_staff(email="staff@test.com", **kwargs):
        user_data = {
            "email": email,
            "first_name": kwargs.get("first_name", "Test"),
            "last_name": kwargs.get("last_name", "Staff"),
        }
        return SchoolUser.objects.create_staff(**user_data)
    
    return _create_staff


# Pre-created User Fixtures
@pytest.fixture
def student_user(create_student):
    """Create a single student user for testing."""
    return create_student(email="john.student@school.com", first_name="John", last_name="Doe")


@pytest.fixture
def parent_user(create_parent):
    """Create a single parent user for testing."""
    return create_parent(email="jane.parent@school.com", first_name="Jane", last_name="Doe")


@pytest.fixture
def teacher_user(create_teacher):
    """Create a single teacher user for testing."""
    return create_teacher(email="mike.teacher@school.com", first_name="Mike", last_name="Smith")


@pytest.fixture
def principal_user(create_principal):
    """Create a single principal user for testing."""
    return create_principal(email="robert.principal@school.com", first_name="Robert", last_name="Johnson")


@pytest.fixture
def vp_user(create_vp):
    """Create a single VP user for testing."""
    return create_vp(email="sarah.vp@school.com", first_name="Sarah", last_name="Williams")


@pytest.fixture
def staff_user(create_staff):
    """Create a single staff user for testing."""
    return create_staff(email="anna.staff@school.com", first_name="Anna", last_name="Brown")


# Profile Fixtures
@pytest.fixture
def student_profile(student_user):
    """Get the student profile for the student user."""
    return student_user.student


@pytest.fixture
def parent_profile(parent_user):
    """Get the parent profile for the parent user."""
    return parent_user.parent


@pytest.fixture
def teacher_profile(teacher_user):
    """Get the school staff profile for the teacher user."""
    return teacher_user.schoolstaff


# Multiple Users Fixtures
@pytest.fixture
def multiple_students(create_student):
    """Create multiple students for testing relationships."""
    return [
        create_student(email=f"student{i}@school.com", first_name=f"Student{i}", last_name="Test")
        for i in range(1, 4)
    ]


@pytest.fixture
def multiple_teachers(create_teacher):
    """Create multiple teachers for testing staff queries."""
    return [
        create_teacher(email=f"teacher{i}@school.com", first_name=f"Teacher{i}", last_name="Test")
        for i in range(1, 4)
    ]


# Family Fixture - Parent with Children
@pytest.fixture
def family(create_parent, create_student):
    """Create a parent with multiple children for testing relationships."""
    parent = create_parent(email="parent@family.com", first_name="Parent", last_name="Family")
    child1 = create_student(email="child1@family.com", first_name="Child1", last_name="Family")
    child2 = create_student(email="child2@family.com", first_name="Child2", last_name="Family")
    
    parent.parent.add_child(child1)
    parent.parent.add_child(child2)
    
    return {
        "parent": parent,
        "children": [child1, child2],
    }


# Plain User Fixture (without profile)
@pytest.fixture
def plain_user(db):
    """Create a plain user without any profile for testing profile creation."""
    return User.objects.create_user(
        email="plain@test.com",
        first_name="Plain",
        last_name="User",
        password="TestPass123!"
    )
