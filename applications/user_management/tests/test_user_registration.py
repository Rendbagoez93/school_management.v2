"""
Test User Registration Use Cases

This module tests real-world user registration scenarios:
1. Registering a New Student
2. Registering a Parent
4. Hiring a Teacher

These tests verify proper user creation, profile assignment, and group membership.
"""

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db import IntegrityError

from config.roles import RoleEnum
from applications.user_management.models import Parent, SchoolStaff, SchoolUser, Student

User = get_user_model()


@pytest.mark.django_db
class TestStudentRegistration:
    """
    Use Case 1: Registering a New Student
    
    Flow: Admin / Admission Officer creates a new student account
    
    System Expectations:
    ✔ User created
    ✔ Student profile created
    ✔ User added to STUDENT group
    ✔ No other profiles allowed
    
    Validation Rules:
    ✔ Cannot already be Parent
    ✔ Cannot already be Staff
    ✔ Cannot already be Student
    """
    
    def test_student_registration_success(self, student_user_data, student_group):
        """Test successful student registration creates user, profile, and group membership."""
        # Act: Admin/Admission Officer registers a new student
        student = SchoolUser.objects.create_student(**student_user_data)
        
        # Assert: User is created
        assert student is not None
        assert student.email == student_user_data["email"]
        assert student.first_name == student_user_data["first_name"]
        assert student.last_name == student_user_data["last_name"]
        
        # Assert: Student profile is created
        assert hasattr(student, "student")
        assert student.student is not None
        assert isinstance(student.student, Student)
        
        # Assert: User is added to STUDENT group
        assert student.groups.filter(name=RoleEnum.STUDENT.value).exists()
        assert student_group in student.groups.all()
        
        # Assert: User is a regular user, not staff
        assert student.is_staff is False
        assert student.is_superuser is False
        
    def test_student_has_only_student_profile(self, student_user_data):
        """Test that student has only Student profile and no other profiles."""
        # Act: Create student
        student = SchoolUser.objects.create_student(**student_user_data)
        
        # Assert: Has Student profile
        assert hasattr(student, "student")
        assert student.student is not None
        
        # Assert: No Parent profile
        with pytest.raises(AttributeError):
            _ = student.parent
        
        # Assert: No SchoolStaff profile
        with pytest.raises(AttributeError):
            _ = student.schoolstaff
    
    def test_student_cannot_already_be_parent(self, create_parent):
        """Test that a parent user cannot be registered as a student."""
        # Arrange: Create a parent user
        parent = create_parent(email="parent.student@school.com")
        
        # Act & Assert: Attempt to create Student profile for existing parent should fail
        with pytest.raises(IntegrityError, match="already has a Parent profile"):
            Student.objects.create(user=parent)
    
    def test_student_cannot_already_be_staff(self, create_teacher):
        """Test that a staff user cannot be registered as a student."""
        # Arrange: Create a teacher (staff) user
        teacher = create_teacher(email="teacher.student@school.com")
        
        # Act & Assert: Attempt to create Student profile for existing staff should fail
        with pytest.raises(IntegrityError, match="already has a SchoolStaff profile"):
            Student.objects.create(user=teacher)
    
    def test_student_cannot_be_registered_twice(self, student_user):
        """Test that a student cannot be registered twice."""
        # Arrange: Student already exists
        assert student_user.student is not None
        
        # Act & Assert: Attempt to create another Student profile should fail
        with pytest.raises(IntegrityError, match="already has a Student profile"):
            Student.objects.create(user=student_user)
    
    def test_multiple_students_can_be_created(self):
        """Test that multiple students can be registered independently."""
        # Act: Create multiple students
        student1 = SchoolUser.objects.create_student(
            email="student1@school.com",
            first_name="John",
            last_name="Doe"
        )
        student2 = SchoolUser.objects.create_student(
            email="student2@school.com",
            first_name="Jane",
            last_name="Smith"
        )
        student3 = SchoolUser.objects.create_student(
            email="student3@school.com",
            first_name="Bob",
            last_name="Johnson"
        )
        
        # Assert: All students are created successfully
        assert Student.objects.count() == 3
        assert student1.student is not None
        assert student2.student is not None
        assert student3.student is not None
        
        # Assert: All are in STUDENT group
        assert all(
            user.groups.filter(name=RoleEnum.STUDENT.value).exists()
            for user in [student1, student2, student3]
        )


@pytest.mark.django_db
class TestParentRegistration:
    """
    Use Case 2: Registering a Parent
    
    Expectations:
    ✔ Normal user (not staffuser)
    ✔ Parent profile created
    ✔ Added to PARENT group
    ✔ No staff privileges
    
    Important Business Logic:
    ✔ Parents typically should not be staffusers
    """
    
    def test_parent_registration_success(self, parent_user_data, parent_group):
        """Test successful parent registration creates user, profile, and group membership."""
        # Act: Register a new parent
        parent = SchoolUser.objects.create_parent(**parent_user_data)
        
        # Assert: User is created
        assert parent is not None
        assert parent.email == parent_user_data["email"]
        assert parent.first_name == parent_user_data["first_name"]
        assert parent.last_name == parent_user_data["last_name"]
        
        # Assert: Parent profile is created
        assert hasattr(parent, "parent")
        assert parent.parent is not None
        assert isinstance(parent.parent, Parent)
        
        # Assert: User is added to PARENT group
        assert parent.groups.filter(name=RoleEnum.PARENT.value).exists()
        assert parent_group in parent.groups.all()
    
    def test_parent_is_not_staff_user(self, parent_user_data):
        """Test that parent is a normal user, not a staff user."""
        # Act: Create parent
        parent = SchoolUser.objects.create_parent(**parent_user_data)
        
        # Assert: Parent is NOT a staff user
        assert parent.is_staff is False
        assert parent.is_superuser is False
    
    def test_parent_has_no_staff_privileges(self, parent_user):
        """Test that parent has no staff-level privileges."""
        # Assert: Parent has no staff privileges
        assert parent_user.is_staff is False
        assert parent_user.is_superuser is False
        
        # Assert: Parent is in PARENT group, not staff groups
        assert parent_user.groups.filter(name=RoleEnum.PARENT.value).exists()
        assert not parent_user.groups.filter(name=RoleEnum.TEACHER.value).exists()
        assert not parent_user.groups.filter(name=RoleEnum.PRINCIPAL.value).exists()
    
    def test_parent_profile_initialized_with_empty_children(self, parent_user):
        """Test that new parent profile has no children initially."""
        # Assert: Parent has no children initially
        assert parent_user.parent.children.count() == 0
        assert list(parent_user.parent.get_children_list()) == []
    
    def test_multiple_parents_can_be_created(self):
        """Test that multiple parents can be registered independently."""
        # Act: Create multiple parents
        parent1 = SchoolUser.objects.create_parent(email="parent1@school.com")
        parent2 = SchoolUser.objects.create_parent(email="parent2@school.com")
        
        # Assert: All parents are created successfully
        assert Parent.objects.count() == 2
        assert parent1.parent is not None
        assert parent2.parent is not None


@pytest.mark.django_db
class TestTeacherHiring:
    """
    Use Case 4: Hiring a Teacher
    
    Expectations:
    ✔ Staffuser created
    ✔ SchoolStaff profile created
    ✔ Added to TEACHER group
    
    Architectural Strength:
    ✔ Teacher is a specialization of SchoolStaff
    """
    
    def test_teacher_hiring_success(self, teacher_user_data, teacher_group):
        """Test successful teacher hiring creates staffuser, profile, and group membership."""
        # Act: Hire a new teacher
        teacher = SchoolUser.objects.create_teacher(**teacher_user_data)
        
        # Assert: User is created
        assert teacher is not None
        assert teacher.email == teacher_user_data["email"]
        assert teacher.first_name == teacher_user_data["first_name"]
        assert teacher.last_name == teacher_user_data["last_name"]
        
        # Assert: SchoolStaff profile is created
        assert hasattr(teacher, "schoolstaff")
        assert teacher.schoolstaff is not None
        assert isinstance(teacher.schoolstaff, SchoolStaff)
        
        # Assert: User is added to TEACHER group
        assert teacher.groups.filter(name=RoleEnum.TEACHER.value).exists()
        assert teacher_group in teacher.groups.all()
    
    def test_teacher_is_staff_user(self, teacher_user_data):
        """Test that teacher is created as a staff user."""
        # Act: Hire teacher
        teacher = SchoolUser.objects.create_teacher(**teacher_user_data)
        
        # Assert: Teacher IS a staff user (has Django admin access)
        assert teacher.is_staff is True
        assert teacher.is_superuser is False
    
    def test_teacher_is_specialization_of_school_staff(self, teacher_user):
        """Test architectural strength: Teacher is a type of SchoolStaff."""
        # Assert: Teacher has SchoolStaff profile
        assert hasattr(teacher_user, "schoolstaff")
        assert teacher_user.schoolstaff is not None
        
        # Assert: Teacher is in TEACHER group (specialization)
        assert teacher_user.groups.filter(name=RoleEnum.TEACHER.value).exists()
        
        # Assert: SchoolStaff profile can accommodate different staff types
        staff_profile = teacher_user.schoolstaff
        assert isinstance(staff_profile, SchoolStaff)
        
        # Note: The same SchoolStaff model serves Teachers, Principals, VP, etc.
        # Group membership determines the specific role
    
    def test_multiple_teachers_can_be_hired(self, create_teacher):
        """Test that multiple teachers can be hired independently."""
        # Act: Hire multiple teachers
        teacher1 = create_teacher(email="math.teacher@school.com", first_name="Math")
        teacher2 = create_teacher(email="english.teacher@school.com", first_name="English")
        teacher3 = create_teacher(email="science.teacher@school.com", first_name="Science")
        
        # Assert: All teachers are created successfully
        teachers = SchoolUser.objects.get_teachers()
        assert teachers.count() == 3
        
        # Assert: All have SchoolStaff profiles
        assert all(hasattr(t, "schoolstaff") for t in [teacher1, teacher2, teacher3])
        
        # Assert: All are staff users
        assert all(t.is_staff for t in [teacher1, teacher2, teacher3])
    
    def test_teacher_cannot_be_student(self, student_user):
        """Test that a student cannot be hired as a teacher."""
        # Arrange: Student already exists
        assert student_user.student is not None
        
        # Act & Assert: Attempt to create SchoolStaff profile should fail
        with pytest.raises(IntegrityError, match="already has a Student profile"):
            SchoolStaff.objects.create(user=student_user)
    
    def test_teacher_cannot_be_parent(self, parent_user):
        """Test that a parent cannot be hired as a teacher."""
        # Arrange: Parent already exists
        assert parent_user.parent is not None
        
        # Act & Assert: Attempt to create SchoolStaff profile should fail
        with pytest.raises(IntegrityError, match="already has a Parent profile"):
            SchoolStaff.objects.create(user=parent_user)


@pytest.mark.django_db
class TestUserRegistrationEdgeCases:
    """Additional edge cases for user registration."""
    
    def test_email_uniqueness_enforced(self, create_student):
        """Test that email uniqueness is enforced across all user types."""
        # Arrange: Create a student with specific email
        email = "unique@school.com"
        create_student(email=email)
        
        # Act & Assert: Attempt to create another user with same email should fail
        with pytest.raises(IntegrityError):
            SchoolUser.objects.create_parent(email=email)
    
    def test_user_created_with_correct_defaults(self, student_user):
        """Test that users are created with correct default values."""
        # Assert: Default values are set correctly
        assert student_user.is_active is True
        assert student_user.is_verified is False
        assert student_user.date_joined is not None
    
    def test_user_full_name_generation(self, student_user_data):
        """Test that user's full name is generated correctly."""
        # Act: Create user
        student = SchoolUser.objects.create_student(**student_user_data)
        
        # Assert: Full name is correctly generated
        expected_full_name = f"{student_user_data['first_name']} {student_user_data['last_name']}"
        assert student.get_full_name() == expected_full_name
