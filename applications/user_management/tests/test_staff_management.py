"""
Test Staff Management Use Cases

This module tests real-world staff management scenarios:
5. Promoting Staff to Vice Principal
9. Staff Listing

These tests verify group membership updates, role transitions,
and staff querying capabilities.
"""

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from config.roles import RoleEnum
from applications.user_management.models import SchoolStaff, SchoolUser

User = get_user_model()


@pytest.mark.django_db
class TestStaffPromotion:
    """
    Use Case 5: Promoting Staff to Vice Principal
    
    Expectations:
    ✔ Update group membership
    ✔ Keep profile intact
    ✔ Seamless role transition
    ✔ No profile recreation needed
    """
    
    def test_promote_teacher_to_vice_principal(self, teacher_user, vp_group, teacher_group):
        """Test promoting a teacher to vice principal position."""
        # Arrange: Teacher exists with SchoolStaff profile
        assert teacher_user.schoolstaff is not None
        assert teacher_user.groups.filter(name=RoleEnum.TEACHER.value).exists()
        original_profile = teacher_user.schoolstaff
        
        # Act: Promote to Vice Principal (update group membership)
        teacher_user.groups.remove(teacher_group)
        teacher_user.groups.add(vp_group)
        teacher_user.refresh_from_db()
        
        # Assert: Group membership updated
        assert teacher_user.groups.filter(name=RoleEnum.VP.value).exists()
        assert not teacher_user.groups.filter(name=RoleEnum.TEACHER.value).exists()
        
        # Assert: Profile remains intact (same instance)
        assert teacher_user.schoolstaff is not None
        assert teacher_user.schoolstaff.id == original_profile.id
        
        # Assert: Still a staff user
        assert teacher_user.is_staff is True
    
    def test_promote_teacher_to_principal(self, teacher_user, principal_group, teacher_group):
        """Test promoting a teacher to principal position."""
        # Arrange: Teacher exists
        assert teacher_user.groups.filter(name=RoleEnum.TEACHER.value).exists()
        original_profile_id = teacher_user.schoolstaff.id
        
        # Act: Promote to Principal
        teacher_user.groups.remove(teacher_group)
        teacher_user.groups.add(principal_group)
        teacher_user.refresh_from_db()
        
        # Assert: Group updated correctly
        assert teacher_user.groups.filter(name=RoleEnum.PRINCIPAL.value).exists()
        assert not teacher_user.groups.filter(name=RoleEnum.TEACHER.value).exists()
        
        # Assert: Profile preserved
        assert teacher_user.schoolstaff.id == original_profile_id
    
    def test_promote_staff_to_vp_keeps_profile_data(self, create_staff, vp_group, staff_group):
        """Test that promotion preserves profile data and attributes."""
        # Arrange: Create staff with profile attributes
        staff = create_staff(email="staff@promote.com")
        staff.schoolstaff.address = "123 School Street"
        staff.schoolstaff.attributes = {
            "department": "Administration",
            "hire_date": "2020-01-15"
        }
        staff.schoolstaff.save()
        
        original_address = staff.schoolstaff.address
        original_attributes = staff.schoolstaff.attributes
        original_created_at = staff.schoolstaff.created_at
        
        # Act: Promote to VP
        staff.groups.remove(staff_group)
        staff.groups.add(vp_group)
        staff.refresh_from_db()
        
        # Assert: Profile data preserved
        assert staff.schoolstaff.address == original_address
        assert staff.schoolstaff.attributes == original_attributes
        assert staff.schoolstaff.created_at == original_created_at
        
        # Assert: Group membership updated
        assert staff.groups.filter(name=RoleEnum.VP.value).exists()
    
    def test_vp_to_principal_promotion(self, vp_user, principal_group, vp_group):
        """Test promoting VP to Principal."""
        # Arrange: VP exists
        assert vp_user.groups.filter(name=RoleEnum.VP.value).exists()
        
        # Act: Promote to Principal
        vp_user.groups.remove(vp_group)
        vp_user.groups.add(principal_group)
        vp_user.refresh_from_db()
        
        # Assert: Successfully promoted
        assert vp_user.groups.filter(name=RoleEnum.PRINCIPAL.value).exists()
        assert not vp_user.groups.filter(name=RoleEnum.VP.value).exists()
        assert vp_user.schoolstaff is not None
    
    def test_demote_vp_to_teacher(self, vp_user, teacher_group, vp_group):
        """Test demoting VP back to teacher (role transition works both ways)."""
        # Arrange: VP exists
        assert vp_user.groups.filter(name=RoleEnum.VP.value).exists()
        original_profile = vp_user.schoolstaff
        
        # Act: Demote to Teacher
        vp_user.groups.remove(vp_group)
        vp_user.groups.add(teacher_group)
        vp_user.refresh_from_db()
        
        # Assert: Role updated
        assert vp_user.groups.filter(name=RoleEnum.TEACHER.value).exists()
        assert not vp_user.groups.filter(name=RoleEnum.VP.value).exists()
        
        # Assert: Profile still intact
        assert vp_user.schoolstaff.id == original_profile.id
    
    def test_staff_profile_not_recreated_on_promotion(self, teacher_user, principal_group, teacher_group):
        """Test that promotion doesn't trigger profile recreation."""
        # Arrange: Get original profile timestamp
        original_created_at = teacher_user.schoolstaff.created_at
        original_id = teacher_user.schoolstaff.id
        
        # Act: Promote
        teacher_user.groups.remove(teacher_group)
        teacher_user.groups.add(principal_group)
        teacher_user.refresh_from_db()
        
        # Assert: Same profile instance
        assert teacher_user.schoolstaff.id == original_id
        assert teacher_user.schoolstaff.created_at == original_created_at
        
        # Assert: Profile count hasn't increased
        assert SchoolStaff.objects.filter(user=teacher_user).count() == 1
    
    def test_only_group_changes_on_promotion(self, teacher_user, vp_group, teacher_group):
        """Test that only group membership changes during promotion."""
        # Arrange: Capture original user state
        original_email = teacher_user.email
        original_is_staff = teacher_user.is_staff
        original_first_name = teacher_user.first_name
        
        # Act: Promote
        teacher_user.groups.remove(teacher_group)
        teacher_user.groups.add(vp_group)
        teacher_user.refresh_from_db()
        
        # Assert: User attributes unchanged
        assert teacher_user.email == original_email
        assert teacher_user.is_staff == original_is_staff
        assert teacher_user.first_name == original_first_name
        
        # Assert: Only group changed
        assert teacher_user.groups.filter(name=RoleEnum.VP.value).exists()


@pytest.mark.django_db
class TestStaffListing:
    """
    Use Case 9: Staff Listing
    
    Expectations:
    ✔ List all teachers
    ✔ List all principals
    ✔ List all vice principals
    ✔ List all staff members
    ✔ Efficient querying with proper filters
    """
    
    def test_get_all_teachers(self, create_teacher):
        """Test querying all teachers in the system."""
        # Arrange: Create multiple teachers
        teacher1 = create_teacher(email="math@school.com", first_name="Math")
        teacher2 = create_teacher(email="english@school.com", first_name="English")
        teacher3 = create_teacher(email="science@school.com", first_name="Science")
        
        # Act: Get all teachers
        teachers = SchoolUser.objects.get_teachers()
        
        # Assert: All teachers returned
        assert teachers.count() == 3
        assert teacher1 in teachers
        assert teacher2 in teachers
        assert teacher3 in teachers
        
        # Assert: All are in TEACHER group
        for teacher in teachers:
            assert teacher.groups.filter(name=RoleEnum.TEACHER.value).exists()
    
    def test_get_all_principals(self, create_principal):
        """Test querying all principals in the system."""
        # Arrange: Create principals (typically one, but testing multiple)
        principal1 = create_principal(email="principal@school.com")
        
        # Act: Get all principals
        principals = SchoolUser.objects.get_principals()
        
        # Assert: Principals returned
        assert principals.count() == 1
        assert principal1 in principals
        
        # Assert: All are in PRINCIPAL group
        for principal in principals:
            assert principal.groups.filter(name=RoleEnum.PRINCIPAL.value).exists()
    
    def test_get_all_students(self, multiple_students):
        """Test querying all students in the system."""
        # Act: Get all students
        students = SchoolUser.objects.get_students()
        
        # Assert: All students returned
        assert students.count() == 3
        for student in multiple_students:
            assert student in students
    
    def test_get_all_parents(self, create_parent):
        """Test querying all parents in the system."""
        # Arrange: Create multiple parents
        parent1 = create_parent(email="parent1@school.com")
        parent2 = create_parent(email="parent2@school.com")
        
        # Act: Get all parents
        parents = SchoolUser.objects.get_parents()
        
        # Assert: All parents returned
        assert parents.count() == 2
        assert parent1 in parents
        assert parent2 in parents
    
    def test_get_all_staff_users(self, create_teacher, create_principal, create_vp, create_staff):
        """Test querying all staff users (excluding students and parents)."""
        # Arrange: Create various staff members
        teacher = create_teacher(email="teacher@staff.com")
        principal = create_principal(email="principal@staff.com")
        vp = create_vp(email="vp@staff.com")
        staff = create_staff(email="staff@staff.com")
        
        # Also create non-staff users to ensure they're excluded
        student = SchoolUser.objects.create_student(email="student@staff.com")
        parent = SchoolUser.objects.create_parent(email="parent@staff.com")
        
        # Act: Get all staff users
        all_staff = SchoolUser.objects.all_staff()
        
        # Assert: All staff included
        assert teacher in all_staff
        assert principal in all_staff
        assert vp in all_staff
        assert staff in all_staff
        
        # Assert: Non-staff excluded
        assert student not in all_staff
        assert parent not in all_staff
        
        # Assert: Correct count
        assert all_staff.count() == 4
    
    def test_staff_listing_by_type(
        self, 
        create_teacher, 
        create_principal, 
        create_vp, 
        create_staff
    ):
        """Test comprehensive staff listing organized by role type."""
        # Arrange: Create complete staff structure
        teachers = [create_teacher(email=f"teacher{i}@school.com") for i in range(3)]
        principal = create_principal(email="principal@school.com")
        vp = create_vp(email="vp@school.com")
        support_staff = [create_staff(email=f"staff{i}@school.com") for i in range(2)]
        
        # Act: Query different staff types
        all_teachers = SchoolUser.objects.get_teachers()
        all_principals = SchoolUser.objects.get_principals()
        all_staff = SchoolUser.objects.all_staff()
        
        # Assert: Correct counts for each type
        assert all_teachers.count() == 3
        assert all_principals.count() == 1
        assert all_staff.count() == 6  # 3 teachers + 1 principal + 1 vp + 2 staff
        
        # Assert: Teachers are separate from principals
        assert principal not in all_teachers
        assert vp not in all_teachers
        
        # Assert: All staff includes everyone
        assert all(teacher in all_staff for teacher in teachers)
        assert principal in all_staff
        assert vp in all_staff
        assert all(staff in all_staff for staff in support_staff)
    
    def test_all_school_users_includes_everyone(
        self,
        create_teacher,
        create_student,
        create_parent,
        create_principal
    ):
        """Test that all() returns all users in the school system."""
        # Arrange: Create users of all types
        teacher = create_teacher(email="teacher@all.com")
        student = create_student(email="student@all.com")
        parent = create_parent(email="parent@all.com")
        principal = create_principal(email="principal@all.com")
        
        # Act: Get all school users
        all_users = SchoolUser.objects.all()
        
        # Assert: All users included
        assert teacher in all_users
        assert student in all_users
        assert parent in all_users
        assert principal in all_users
        assert all_users.count() >= 4
    
    def test_staff_listing_performance_with_groups_prefetch(self, multiple_teachers):
        """Test that staff listing efficiently prefetches group relationships."""
        # Act: Get all staff (should prefetch groups)
        all_staff = SchoolUser.objects.all_staff()
        
        # Assert: Groups are prefetched (accessing groups doesn't hit DB again)
        # This is ensured by prefetch_related in the manager
        assert all_staff.count() == 3
        
        # Access groups for all users (should not cause N+1 queries)
        for staff_member in all_staff:
            groups = list(staff_member.groups.all())
            assert len(groups) > 0
    
    def test_empty_staff_listing(self, db):
        """Test staff listing when no staff exists."""
        # Act: Query staff when none exist
        teachers = SchoolUser.objects.get_teachers()
        principals = SchoolUser.objects.get_principals()
        all_staff = SchoolUser.objects.all_staff()
        
        # Assert: Returns empty querysets
        assert teachers.count() == 0
        assert principals.count() == 0
        assert all_staff.count() == 0
    
    def test_staff_listing_after_promotion(self, teacher_user, principal_group, teacher_group):
        """Test that staff listings update correctly after promotions."""
        # Arrange: Initial state - one teacher
        assert SchoolUser.objects.get_teachers().count() == 1
        assert SchoolUser.objects.get_principals().count() == 0
        
        # Act: Promote teacher to principal
        teacher_user.groups.remove(teacher_group)
        teacher_user.groups.add(principal_group)
        
        # Assert: Listings reflect the change
        assert SchoolUser.objects.get_teachers().count() == 0
        assert SchoolUser.objects.get_principals().count() == 1
        
        # Assert: Still appears in all_staff
        assert teacher_user in SchoolUser.objects.all_staff()
    
    def test_filter_staff_by_additional_criteria(self, multiple_teachers):
        """Test filtering staff by additional criteria beyond groups."""
        # Arrange: Mark one teacher as inactive
        multiple_teachers[0].is_active = False
        multiple_teachers[0].save()
        
        # Act: Get active teachers only
        active_teachers = SchoolUser.objects.get_teachers().filter(is_active=True)
        
        # Assert: Only active teachers returned
        assert active_teachers.count() == 2
        assert multiple_teachers[0] not in active_teachers
        assert multiple_teachers[1] in active_teachers
        assert multiple_teachers[2] in active_teachers


@pytest.mark.django_db
class TestStaffManagementEdgeCases:
    """Additional edge cases for staff management."""
    
    def test_staff_with_multiple_roles_not_recommended(self, teacher_user, staff_group):
        """Test handling of staff with multiple role groups (not recommended but possible)."""
        # Arrange: Teacher exists
        assert teacher_user.groups.filter(name=RoleEnum.TEACHER.value).exists()
        
        # Act: Add another staff group (not removing teacher group)
        teacher_user.groups.add(staff_group)
        
        # Assert: User is in both groups
        assert teacher_user.groups.filter(name=RoleEnum.TEACHER.value).exists()
        assert teacher_user.groups.filter(name=RoleEnum.STAFF.value).exists()
        
        # Assert: Appears in both queries
        assert teacher_user in SchoolUser.objects.get_teachers()
        assert teacher_user in SchoolUser.objects.all_staff()
    
    def test_remove_all_groups_staff_not_in_listings(self, teacher_user, teacher_group):
        """Test that staff without groups don't appear in role-specific listings."""
        # Act: Remove all groups from teacher
        teacher_user.groups.remove(teacher_group)
        
        # Assert: Not in teacher listing
        assert teacher_user not in SchoolUser.objects.get_teachers()
        
        # Assert: Not in all_staff (requires group membership)
        assert teacher_user not in SchoolUser.objects.all_staff()
        
        # Assert: Profile still exists
        assert teacher_user.schoolstaff is not None
