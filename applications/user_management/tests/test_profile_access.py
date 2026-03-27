"""
Test Profile Access and Login-Driven UI Behavior

This module tests real-world profile access scenarios:
7. Login-Driven UI Behavior

These tests verify:
✔ Correct profile object is returned
✔ Parent → Parent dashboard routing
✔ Student → Student dashboard routing  
✔ Staff → Staff dashboard routing
✔ Profile property returns correct profile type
"""

import pytest
from django.contrib.auth import get_user_model

from config.roles import RoleEnum
from applications.user_management.models import Parent, SchoolStaff, SchoolUser, Student

User = get_user_model()


@pytest.mark.django_db
class TestLoginDrivenUIBehavior:
    """
    Use Case 7: Login-Driven UI Behavior
    
    Expectations:
    ✔ Returns correct profile object based on user type
    ✔ Parent → Parent dashboard
    ✔ Student → Student dashboard
    ✔ Staff → Staff dashboard
    
    Real-World Usage:
    After login, system needs to determine which dashboard to show
    based on the user's profile type.
    """
    
    def test_student_login_returns_student_profile(self, student_user):
        """Test that student user returns Student profile for dashboard routing."""
        # Act: Get profile (simulating post-login profile check)
        profile = student_user.profile
        
        # Assert: Returns Student profile instance
        assert isinstance(profile, Student)
        assert profile == student_user.student
        
        # Assert: Can route to student dashboard
        assert student_user.groups.filter(name=RoleEnum.STUDENT.value).exists()
        
        # Real-world usage: if isinstance(user.profile, Student): redirect to student_dashboard
    
    def test_parent_login_returns_parent_profile(self, parent_user):
        """Test that parent user returns Parent profile for dashboard routing."""
        # Act: Get profile (simulating post-login profile check)
        profile = parent_user.profile
        
        # Assert: Returns Parent profile instance
        assert isinstance(profile, Parent)
        assert profile == parent_user.parent
        
        # Assert: Can route to parent dashboard
        assert parent_user.groups.filter(name=RoleEnum.PARENT.value).exists()
        
        # Real-world usage: if isinstance(user.profile, Parent): redirect to parent_dashboard
    
    def test_teacher_login_returns_staff_profile(self, teacher_user):
        """Test that teacher user returns SchoolStaff profile for dashboard routing."""
        # Act: Get profile (simulating post-login profile check)
        profile = teacher_user.profile
        
        # Assert: Returns SchoolStaff profile instance
        assert isinstance(profile, SchoolStaff)
        assert profile == teacher_user.schoolstaff
        
        # Assert: Can route to staff dashboard
        assert teacher_user.groups.filter(name=RoleEnum.TEACHER.value).exists()
        
        # Real-world usage: if isinstance(user.profile, SchoolStaff): redirect to staff_dashboard
    
    def test_principal_login_returns_staff_profile(self, principal_user):
        """Test that principal user returns SchoolStaff profile for admin dashboard routing."""
        # Act: Get profile
        profile = principal_user.profile
        
        # Assert: Returns SchoolStaff profile instance
        assert isinstance(profile, SchoolStaff)
        assert profile == principal_user.schoolstaff
        
        # Assert: Can route to principal/admin dashboard
        assert principal_user.groups.filter(name=RoleEnum.PRINCIPAL.value).exists()
    
    def test_vp_login_returns_staff_profile(self, vp_user):
        """Test that VP user returns SchoolStaff profile for admin dashboard routing."""
        # Act: Get profile
        profile = vp_user.profile
        
        # Assert: Returns SchoolStaff profile instance
        assert isinstance(profile, SchoolStaff)
        assert profile == vp_user.schoolstaff
        
        # Assert: Can route to VP dashboard
        assert vp_user.groups.filter(name=RoleEnum.VP.value).exists()


@pytest.mark.django_db
class TestProfilePropertyBehavior:
    """Test the profile property specifically."""
    
    def test_profile_property_for_student(self, student_user):
        """Test profile property returns Student for student users."""
        # Act & Assert
        assert hasattr(student_user, "profile")
        assert student_user.profile == student_user.student
        assert isinstance(student_user.profile, Student)
    
    def test_profile_property_for_parent(self, parent_user):
        """Test profile property returns Parent for parent users."""
        # Act & Assert
        assert hasattr(parent_user, "profile")
        assert parent_user.profile == parent_user.parent
        assert isinstance(parent_user.profile, Parent)
    
    def test_profile_property_for_staff(self, teacher_user):
        """Test profile property returns SchoolStaff for staff users."""
        # Act & Assert
        assert hasattr(teacher_user, "profile")
        assert teacher_user.profile == teacher_user.schoolstaff
        assert isinstance(teacher_user.profile, SchoolStaff)
    
    def test_profile_property_raises_error_when_no_profile(self, plain_user):
        """Test that profile property raises AttributeError when user has no profile."""
        # Act & Assert: Accessing profile without creating one raises error
        # Note: User model doesn't have profile property; only SchoolUser proxy does
        with pytest.raises(AttributeError):
            _ = plain_user.profile


@pytest.mark.django_db
class TestDashboardRouting:
    """
    Simulate real-world dashboard routing logic based on profile type.
    
    This demonstrates how the profile property would be used in views
    to determine which dashboard to display.
    """
    
    def test_route_to_correct_dashboard_based_on_profile(
        self, student_user, parent_user, teacher_user
    ):
        """Test dashboard routing logic for different user types."""
        
        def get_dashboard_url(user):
            """Simulated dashboard routing function."""
            profile = user.profile
            
            if isinstance(profile, Student):
                return "/student/dashboard/"
            elif isinstance(profile, Parent):
                return "/parent/dashboard/"
            elif isinstance(profile, SchoolStaff):
                return "/staff/dashboard/"
            else:
                return "/error/"
        
        # Act: Get dashboard URLs for different users
        student_url = get_dashboard_url(student_user)
        parent_url = get_dashboard_url(parent_user)
        teacher_url = get_dashboard_url(teacher_user)
        
        # Assert: Correct dashboards returned
        assert student_url == "/student/dashboard/"
        assert parent_url == "/parent/dashboard/"
        assert teacher_url == "/staff/dashboard/"
    
    def test_dashboard_with_role_specific_features(self, teacher_user, principal_user):
        """Test that dashboard can further customize based on specific role within staff."""
        
        def get_staff_dashboard_features(user):
            """Get dashboard features based on staff role."""
            profile = user.profile
            
            if not isinstance(profile, SchoolStaff):
                return []
            
            features = ["view_schedule", "view_profile"]
            
            # Add role-specific features based on groups
            if user.groups.filter(name=RoleEnum.TEACHER.value).exists():
                features.extend(["manage_classes", "grade_students", "view_timetable"])
            
            if user.groups.filter(name=RoleEnum.PRINCIPAL.value).exists():
                features.extend([
                    "manage_staff", 
                    "manage_students", 
                    "view_reports",
                    "system_settings"
                ])
            
            if user.groups.filter(name=RoleEnum.VP.value).exists():
                features.extend(["manage_staff", "view_reports"])
            
            return features
        
        # Act: Get features for different staff types
        teacher_features = get_staff_dashboard_features(teacher_user)
        principal_features = get_staff_dashboard_features(principal_user)
        
        # Assert: Teacher has teacher-specific features
        assert "manage_classes" in teacher_features
        assert "grade_students" in teacher_features
        assert "system_settings" not in teacher_features
        
        # Assert: Principal has admin features
        assert "manage_staff" in principal_features
        assert "system_settings" in principal_features
        assert "view_reports" in principal_features
    
    def test_parent_dashboard_with_children_access(self, family):
        """Test parent dashboard with access to children's information."""
        
        def get_parent_dashboard_data(user):
            """Simulated parent dashboard data retrieval."""
            profile = user.profile
            
            if not isinstance(profile, Parent):
                return None
            
            children = profile.get_children_list()
            
            return {
                "user": user,
                "profile_type": "Parent",
                "children_count": children.count(),
                "children": [
                    {
                        "name": child.get_full_name(),
                        "email": child.email,
                    }
                    for child in children
                ],
                "features": ["view_children", "view_grades", "contact_teachers"]
            }
        
        # Act: Get parent dashboard data
        parent = family["parent"]
        dashboard_data = get_parent_dashboard_data(parent)
        
        # Assert: Dashboard data includes children information
        assert dashboard_data is not None
        assert dashboard_data["profile_type"] == "Parent"
        assert dashboard_data["children_count"] == 2
        assert len(dashboard_data["children"]) == 2
        assert "view_children" in dashboard_data["features"]
    
    def test_student_dashboard_with_profile_info(self, student_user):
        """Test student dashboard with student-specific information."""
        
        def get_student_dashboard_data(user):
            """Simulated student dashboard data retrieval."""
            profile = user.profile
            
            if not isinstance(profile, Student):
                return None
            
            return {
                "user": user,
                "profile_type": "Student",
                "full_name": user.get_full_name(),
                "email": user.email,
                "features": [
                    "view_schedule",
                    "view_grades",
                    "submit_assignments",
                    "view_announcements"
                ]
            }
        
        # Act: Get student dashboard data
        dashboard_data = get_student_dashboard_data(student_user)
        
        # Assert: Dashboard data is correct
        assert dashboard_data is not None
        assert dashboard_data["profile_type"] == "Student"
        assert "view_grades" in dashboard_data["features"]
        assert "submit_assignments" in dashboard_data["features"]


@pytest.mark.django_db
class TestDirectProfileAccess:
    """
    Test direct profile access as an alternative to the profile property.
    
    NOTE: The models include a note about preferring direct access
    (user.parent, user.student, user.schoolstaff) over the profile property.
    """
    
    def test_direct_student_access(self, student_user):
        """Test accessing student profile directly via user.student."""
        # Act: Access directly
        student_profile = student_user.student
        
        # Assert: Direct access works
        assert student_profile is not None
        assert isinstance(student_profile, Student)
        
        # Assert: Same as profile property
        assert student_profile == student_user.profile
    
    def test_direct_parent_access(self, parent_user):
        """Test accessing parent profile directly via user.parent."""
        # Act: Access directly
        parent_profile = parent_user.parent
        
        # Assert: Direct access works
        assert parent_profile is not None
        assert isinstance(parent_profile, Parent)
        
        # Assert: Same as profile property
        assert parent_profile == parent_user.profile
    
    def test_direct_staff_access(self, teacher_user):
        """Test accessing staff profile directly via user.schoolstaff."""
        # Act: Access directly
        staff_profile = teacher_user.schoolstaff
        
        # Assert: Direct access works
        assert staff_profile is not None
        assert isinstance(staff_profile, SchoolStaff)
        
        # Assert: Same as profile property
        assert staff_profile == teacher_user.profile
    
    def test_direct_access_raises_attribute_error_for_missing_profile(self, student_user):
        """Test that direct access raises AttributeError for non-existent profile."""
        # Act & Assert: Accessing non-existent profile raises AttributeError
        with pytest.raises(AttributeError):
            _ = student_user.parent
        
        with pytest.raises(AttributeError):
            _ = student_user.schoolstaff
    
    def test_hasattr_check_for_profile_existence(self, student_user, parent_user):
        """Test using hasattr to check profile existence before access."""
        # Student checks
        assert hasattr(student_user, "student")
        assert not hasattr(student_user, "parent") or not student_user.parent
        
        # Parent checks
        assert hasattr(parent_user, "parent")
        assert not hasattr(parent_user, "student") or not parent_user.student
    
    def test_recommended_direct_access_pattern(self, student_user, parent_user, teacher_user):
        """
        Test recommended pattern for checking user type using direct access.
        
        This is the recommended approach according to model docstring.
        """
        
        def get_user_type(user):
            """Get user type using direct access pattern (recommended)."""
            if hasattr(user, "student") and user.student:
                return "Student"
            elif hasattr(user, "parent") and user.parent:
                return "Parent"
            elif hasattr(user, "schoolstaff") and user.schoolstaff:
                return "Staff"
            else:
                return "Unknown"
        
        # Act: Get user types
        student_type = get_user_type(student_user)
        parent_type = get_user_type(parent_user)
        teacher_type = get_user_type(teacher_user)
        
        # Assert: Correct types returned
        assert student_type == "Student"
        assert parent_type == "Parent"
        assert teacher_type == "Staff"


@pytest.mark.django_db
class TestProfileAccessEdgeCases:
    """Edge cases for profile access."""
    
    def test_profile_access_after_promotion(self, teacher_user, principal_group, teacher_group):
        """Test that profile access still works after role promotion."""
        # Arrange: Get original profile
        original_profile = teacher_user.profile
        
        # Act: Promote to principal
        teacher_user.groups.remove(teacher_group)
        teacher_user.groups.add(principal_group)
        teacher_user.refresh_from_db()
        
        # Assert: Profile access still works and returns same profile
        assert teacher_user.profile is not None
        assert teacher_user.profile.id == original_profile.id
        assert isinstance(teacher_user.profile, SchoolStaff)
    
    def test_profile_string_representation(self, student_user, parent_user, teacher_user):
        """Test string representation of profiles."""
        # Act: Get string representations
        student_str = str(student_user.student)
        parent_str = str(parent_user.parent)
        teacher_str = str(teacher_user.schoolstaff)
        
        # Assert: Contains user's full name
        assert student_user.get_full_name() in student_str
        assert parent_user.get_full_name() in parent_str
        assert teacher_user.get_full_name() in teacher_str
    
    def test_profile_timestamps(self, student_user, parent_user):
        """Test that profiles have proper timestamps."""
        # Assert: Profiles have created_at and updated_at
        assert student_user.student.created_at is not None
        assert student_user.student.updated_at is not None
        
        assert parent_user.parent.created_at is not None
        assert parent_user.parent.updated_at is not None
    
    def test_profile_optional_fields(self, student_user):
        """Test that optional profile fields can be set."""
        # Act: Set optional fields
        student_user.student.address = "123 Test Street"
        student_user.student.attributes = {
            "grade": "10",
            "section": "A",
            "roll_number": "001"
        }
        student_user.student.save()
        
        # Assert: Fields are saved
        student_user.student.refresh_from_db()
        assert student_user.student.address == "123 Test Street"
        assert student_user.student.attributes["grade"] == "10"
        assert student_user.student.attributes["roll_number"] == "001"
