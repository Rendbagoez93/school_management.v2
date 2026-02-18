"""
Test Profile Integrity Use Cases

This module tests profile integrity and one-profile-per-user constraint:
6. Preventing Multiple Profiles

These tests verify that:
✔ One user can only have one profile type
✔ Manager validation prevents duplicate profiles
✔ Database OneToOne constraint enforces uniqueness
✔ IntegrityError is raised on violations
"""

import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError

from applications.user_management.models import Parent, SchoolStaff, SchoolUser, Student

User = get_user_model()


@pytest.mark.django_db
class TestPreventMultipleProfiles:
    """
    Use Case 6: Preventing Multiple Profiles
    
    Expectations:
    ✔ Raises IntegrityError when attempting to create multiple profiles
    
    Because:
    ✔ Manager validation checks for existing profiles
    ✔ OneToOne constraint at database level
    ✔ Application-level validation in BaseUserTypeManager
    """
    
    def test_student_cannot_also_be_parent(self, student_user):
        """Test that a user with Student profile cannot create Parent profile."""
        # Arrange: Student already exists
        assert student_user.student is not None
        
        # Act & Assert: Attempt to create Parent profile raises IntegrityError
        with pytest.raises(IntegrityError, match="already has a Student profile"):
            Parent.objects.create(user=student_user)
        
        # Assert: Only Student profile exists
        assert hasattr(student_user, "student")
        assert Student.objects.filter(user=student_user).count() == 1
    
    def test_student_cannot_also_be_staff(self, student_user):
        """Test that a user with Student profile cannot create SchoolStaff profile."""
        # Arrange: Student already exists
        assert student_user.student is not None
        
        # Act & Assert: Attempt to create SchoolStaff profile raises IntegrityError
        with pytest.raises(IntegrityError, match="already has a Student profile"):
            SchoolStaff.objects.create(user=student_user)
        
        # Assert: Only Student profile exists
        assert Student.objects.filter(user=student_user).count() == 1
    
    def test_parent_cannot_also_be_student(self, parent_user):
        """Test that a user with Parent profile cannot create Student profile."""
        # Arrange: Parent already exists
        assert parent_user.parent is not None
        
        # Act & Assert: Attempt to create Student profile raises IntegrityError
        with pytest.raises(IntegrityError, match="already has a Parent profile"):
            Student.objects.create(user=parent_user)
        
        # Assert: Only Parent profile exists
        assert Parent.objects.filter(user=parent_user).count() == 1
    
    def test_parent_cannot_also_be_staff(self, parent_user):
        """Test that a user with Parent profile cannot create SchoolStaff profile."""
        # Arrange: Parent already exists
        assert parent_user.parent is not None
        
        # Act & Assert: Attempt to create SchoolStaff profile raises IntegrityError
        with pytest.raises(IntegrityError, match="already has a Parent profile"):
            SchoolStaff.objects.create(user=parent_user)
        
        # Assert: Only Parent profile exists
        assert Parent.objects.filter(user=parent_user).count() == 1
    
    def test_staff_cannot_also_be_student(self, teacher_user):
        """Test that a user with SchoolStaff profile cannot create Student profile."""
        # Arrange: Teacher (SchoolStaff) already exists
        assert teacher_user.schoolstaff is not None
        
        # Act & Assert: Attempt to create Student profile raises IntegrityError
        with pytest.raises(IntegrityError, match="already has a SchoolStaff profile"):
            Student.objects.create(user=teacher_user)
        
        # Assert: Only SchoolStaff profile exists
        assert SchoolStaff.objects.filter(user=teacher_user).count() == 1
    
    def test_staff_cannot_also_be_parent(self, teacher_user):
        """Test that a user with SchoolStaff profile cannot create Parent profile."""
        # Arrange: Teacher (SchoolStaff) already exists
        assert teacher_user.schoolstaff is not None
        
        # Act & Assert: Attempt to create Parent profile raises IntegrityError
        with pytest.raises(IntegrityError, match="already has a SchoolStaff profile"):
            Parent.objects.create(user=teacher_user)
        
        # Assert: Only SchoolStaff profile exists
        assert SchoolStaff.objects.filter(user=teacher_user).count() == 1
    
    def test_cannot_create_duplicate_student_profile(self, student_user):
        """Test that a Student cannot have two Student profiles."""
        # Arrange: Student profile already exists
        assert student_user.student is not None
        existing_profile = student_user.student
        
        # Act & Assert: Attempt to create another Student profile raises IntegrityError
        with pytest.raises(IntegrityError, match="already has a Student profile"):
            Student.objects.create(user=student_user)
        
        # Assert: Still only one Student profile
        assert Student.objects.filter(user=student_user).count() == 1
        assert student_user.student.id == existing_profile.id
    
    def test_cannot_create_duplicate_parent_profile(self, parent_user):
        """Test that a Parent cannot have two Parent profiles."""
        # Arrange: Parent profile already exists
        assert parent_user.parent is not None
        existing_profile = parent_user.parent
        
        # Act & Assert: Attempt to create another Parent profile raises IntegrityError
        with pytest.raises(IntegrityError, match="already has a Parent profile"):
            Parent.objects.create(user=parent_user)
        
        # Assert: Still only one Parent profile
        assert Parent.objects.filter(user=parent_user).count() == 1
        assert parent_user.parent.id == existing_profile.id
    
    def test_cannot_create_duplicate_staff_profile(self, teacher_user):
        """Test that a SchoolStaff cannot have two SchoolStaff profiles."""
        # Arrange: SchoolStaff profile already exists
        assert teacher_user.schoolstaff is not None
        existing_profile = teacher_user.schoolstaff
        
        # Act & Assert: Attempt to create another SchoolStaff profile raises IntegrityError
        with pytest.raises(IntegrityError, match="already has a SchoolStaff profile"):
            SchoolStaff.objects.create(user=teacher_user)
        
        # Assert: Still only one SchoolStaff profile
        assert SchoolStaff.objects.filter(user=teacher_user).count() == 1
        assert teacher_user.schoolstaff.id == existing_profile.id


@pytest.mark.django_db
class TestManagerValidation:
    """
    Test BaseUserTypeManager validation logic.
    
    The manager performs application-level validation before
    attempting to create profiles, providing clear error messages.
    """
    
    def test_manager_checks_for_parent_profile(self, parent_user):
        """Test that manager checks for existing Parent profile."""
        # Arrange: Parent exists
        assert hasattr(parent_user, "parent")
        
        # Act & Assert: Manager validation catches the issue
        with pytest.raises(IntegrityError, match="already has a Parent profile"):
            Student.objects.create(user=parent_user)
    
    def test_manager_checks_for_student_profile(self, student_user):
        """Test that manager checks for existing Student profile."""
        # Arrange: Student exists
        assert hasattr(student_user, "student")
        
        # Act & Assert: Manager validation catches the issue
        with pytest.raises(IntegrityError, match="already has a Student profile"):
            Parent.objects.create(user=student_user)
    
    def test_manager_checks_for_staff_profile(self, teacher_user):
        """Test that manager checks for existing SchoolStaff profile."""
        # Arrange: Teacher (SchoolStaff) exists
        assert hasattr(teacher_user, "schoolstaff")
        
        # Act & Assert: Manager validation catches the issue
        with pytest.raises(IntegrityError, match="already has a SchoolStaff profile"):
            Student.objects.create(user=teacher_user)
    
    def test_manager_allows_first_profile_creation(self, plain_user):
        """Test that manager allows creating first profile for user without any profile."""
        # Arrange: User exists without any profile
        assert not hasattr(plain_user, "parent") or not plain_user.parent
        assert not hasattr(plain_user, "student") or not plain_user.student
        assert not hasattr(plain_user, "schoolstaff") or not plain_user.schoolstaff
        
        # Act: Create Student profile (should succeed)
        student_profile = Student.objects.create(user=plain_user)
        
        # Assert: Profile created successfully
        assert student_profile is not None
        plain_user.refresh_from_db()
        assert hasattr(plain_user, "student")
    
    def test_manager_validation_provides_clear_error_message(self, student_user):
        """Test that IntegrityError has clear, informative message."""
        # Act & Assert: Error message includes user and profile type
        with pytest.raises(IntegrityError) as exc_info:
            Parent.objects.create(user=student_user)
        
        error_message = str(exc_info.value)
        assert "already has a Student profile" in error_message
        assert str(student_user) in error_message


@pytest.mark.django_db
class TestDatabaseConstraints:
    """
    Test that OneToOne database constraint enforces profile uniqueness.
    
    This is the final line of defense after application-level validation.
    """
    
    def test_onetoone_constraint_on_student(self, student_user):
        """Test OneToOne constraint prevents duplicate Student profiles at DB level."""
        # Arrange: Student profile exists
        assert student_user.student is not None
        
        # Act & Assert: Even bypassing manager, DB constraint prevents duplicate
        # (This tests the OneToOneField constraint)
        with pytest.raises(IntegrityError):
            # Try to bypass manager validation by using super().create()
            Student.objects.model(user=student_user).save()
    
    def test_onetoone_constraint_on_parent(self, parent_user):
        """Test OneToOne constraint prevents duplicate Parent profiles at DB level."""
        # Arrange: Parent profile exists
        assert parent_user.parent is not None
        
        # Act & Assert: DB constraint prevents duplicate
        with pytest.raises(IntegrityError):
            Parent.objects.model(user=parent_user).save()
    
    def test_onetoone_constraint_on_staff(self, teacher_user):
        """Test OneToOne constraint prevents duplicate SchoolStaff profiles at DB level."""
        # Arrange: SchoolStaff profile exists
        assert teacher_user.schoolstaff is not None
        
        # Act & Assert: DB constraint prevents duplicate
        with pytest.raises(IntegrityError):
            SchoolStaff.objects.model(user=teacher_user).save()


@pytest.mark.django_db
class TestProfileIntegrityEdgeCases:
    """Additional edge cases for profile integrity."""
    
    def test_different_users_can_have_same_profile_type(self, create_student):
        """Test that different users can have the same profile type (Student)."""
        # Act: Create multiple students
        student1 = create_student(email="student1@test.com")
        student2 = create_student(email="student2@test.com")
        
        # Assert: Both have Student profiles
        assert student1.student is not None
        assert student2.student is not None
        assert student1.student.id != student2.student.id
        assert Student.objects.count() == 2
    
    def test_user_must_exist_before_profile_creation(self):
        """Test that profile cannot be created for non-existent user."""
        # Act & Assert: Creating profile without user should fail
        with pytest.raises((IntegrityError, ValueError)):
            Student.objects.create(user=None)
    
    def test_deleting_user_cascades_to_profile(self, student_user):
        """Test that deleting user also deletes associated profile (CASCADE)."""
        # Arrange: Get profile ID before deletion
        profile_id = student_user.student.id
        user_id = student_user.id
        
        # Act: Delete user
        student_user.delete()
        
        # Assert: Profile is also deleted (CASCADE behavior)
        assert not Student.objects.filter(id=profile_id).exists()
        assert not User.objects.filter(id=user_id).exists()
    
    def test_profile_deletion_keeps_user(self, student_user):
        """Test that deleting profile keeps the user intact."""
        # Arrange: Get user ID
        user_id = student_user.id
        
        # Act: Delete student profile
        student_user.student.delete()
        
        # Assert: User still exists
        assert User.objects.filter(id=user_id).exists()
        
        # Assert: Profile is deleted
        student_user.refresh_from_db()
        with pytest.raises(AttributeError):
            _ = student_user.student
    
    def test_recreate_profile_after_deletion(self, student_user):
        """Test that profile can be recreated after deletion."""
        # Arrange: Delete existing profile
        student_user.student.delete()
        student_user.refresh_from_db()
        
        # Act: Create new Student profile
        new_profile = Student.objects.create(user=student_user)
        
        # Assert: New profile created successfully
        assert new_profile is not None
        student_user.refresh_from_db()
        assert student_user.student is not None
    
    def test_change_profile_type_requires_deletion_first(self, student_user):
        """Test that changing profile type requires deleting old profile first."""
        # Arrange: Student exists
        assert student_user.student is not None
        
        # Act & Assert: Cannot create Parent profile while Student exists
        with pytest.raises(IntegrityError, match="already has a Student profile"):
            Parent.objects.create(user=student_user)
        
        # Act: Delete Student profile first
        student_user.student.delete()
        student_user.refresh_from_db()
        
        # Act: Now can create Parent profile
        parent_profile = Parent.objects.create(user=student_user)
        
        # Assert: Successfully changed profile type
        assert parent_profile is not None
        student_user.refresh_from_db()
        assert student_user.parent is not None
    
    def test_profile_unique_per_user_across_all_types(self, plain_user):
        """Test that user can have at most one profile across all profile types."""
        # Act: Create Student profile
        Student.objects.create(user=plain_user)
        plain_user.refresh_from_db()
        
        # Assert: Cannot create any other profile type
        with pytest.raises(IntegrityError):
            Parent.objects.create(user=plain_user)
        
        with pytest.raises(IntegrityError):
            SchoolStaff.objects.create(user=plain_user)
        
        # Assert: Only one profile exists
        assert Student.objects.filter(user=plain_user).count() == 1
        assert Parent.objects.filter(user=plain_user).count() == 0
        assert SchoolStaff.objects.filter(user=plain_user).count() == 0
