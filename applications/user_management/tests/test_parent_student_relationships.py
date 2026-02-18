"""
Test Parent-Student Relationship Use Cases

This module tests real-world parent-student relationship scenarios:
3. Link Parent to Student
8. Parent Viewing Children Data

These tests verify many-to-many relationships, guardian scenarios, 
and parent access to student data.
"""

import pytest
from django.contrib.auth import get_user_model

from config.roles import RoleEnum
from applications.user_management.models import Parent, SchoolUser, Student

User = get_user_model()


@pytest.mark.django_db
class TestParentStudentLinking:
    """
    Use Case 3: Link Parent to Student
    
    Expectations:
    ✔ Many-to-Many relationship created
    ✔ Parent can have multiple children
    ✔ Student can have multiple parents
    
    Real-World Meaning:
    ✔ Father + Mother accounts
    ✔ Guardian scenarios
    ✔ Custody / separated parents
    """
    
    def test_link_parent_to_single_student(self, parent_user, student_user):
        """Test linking a parent to a single student."""
        # Act: Link parent to student
        parent_user.parent.add_child(student_user)
        
        # Assert: Relationship is created
        assert parent_user.parent.children.count() == 1
        assert student_user in parent_user.parent.children.all()
        
        # Assert: Reverse relationship works
        assert parent_user in student_user.parents.all()
        assert student_user.parents.count() == 1
    
    def test_parent_can_have_multiple_children(self, create_parent, create_student):
        """Test that a parent can have multiple children (siblings)."""
        # Arrange: Create one parent and three children
        parent = create_parent(email="parent@family.com")
        child1 = create_student(email="child1@family.com", first_name="Alice")
        child2 = create_student(email="child2@family.com", first_name="Bob")
        child3 = create_student(email="child3@family.com", first_name="Charlie")
        
        # Act: Link all children to parent
        parent.parent.add_child(child1)
        parent.parent.add_child(child2)
        parent.parent.add_child(child3)
        
        # Assert: Parent has three children
        assert parent.parent.children.count() == 3
        assert child1 in parent.parent.children.all()
        assert child2 in parent.parent.children.all()
        assert child3 in parent.parent.children.all()
        
        # Assert: All children show same parent
        assert parent in child1.parents.all()
        assert parent in child2.parents.all()
        assert parent in child3.parents.all()
    
    def test_student_can_have_multiple_parents(self, create_parent, student_user):
        """Test that a student can have multiple parents (e.g., father and mother)."""
        # Arrange: Create father and mother accounts
        father = create_parent(email="father@family.com", first_name="John", last_name="Father")
        mother = create_parent(email="mother@family.com", first_name="Jane", last_name="Mother")
        
        # Act: Link both parents to student
        father.parent.add_child(student_user)
        mother.parent.add_child(student_user)
        
        # Assert: Student has two parents
        assert student_user.parents.count() == 2
        assert father in student_user.parents.all()
        assert mother in student_user.parents.all()
        
        # Assert: Both parents see the child
        assert student_user in father.parent.children.all()
        assert student_user in mother.parent.children.all()
    
    def test_father_mother_scenario(self, create_parent, create_student):
        """Test real-world scenario: Father and Mother accounts for same children."""
        # Arrange: Create family - father, mother, and two children
        father = create_parent(email="father@smith.com", first_name="John", last_name="Smith")
        mother = create_parent(email="mother@smith.com", first_name="Jane", last_name="Smith")
        child1 = create_student(email="son@smith.com", first_name="Tommy", last_name="Smith")
        child2 = create_student(email="daughter@smith.com", first_name="Emma", last_name="Smith")
        
        # Act: Link both parents to both children
        father.parent.add_child(child1)
        father.parent.add_child(child2)
        mother.parent.add_child(child1)
        mother.parent.add_child(child2)
        
        # Assert: Both parents have both children
        assert father.parent.children.count() == 2
        assert mother.parent.children.count() == 2
        
        # Assert: Both children have both parents
        assert child1.parents.count() == 2
        assert child2.parents.count() == 2
        
        # Assert: Family relationships are complete
        assert set(father.parent.children.all()) == {child1, child2}
        assert set(mother.parent.children.all()) == {child1, child2}
        assert set(child1.parents.all()) == {father, mother}
        assert set(child2.parents.all()) == {father, mother}
    
    def test_guardian_scenario(self, create_parent, student_user):
        """Test guardian scenario where non-biological parent has custody."""
        # Arrange: Create guardian account (e.g., grandparent, aunt, foster parent)
        guardian = create_parent(
            email="guardian@example.com",
            first_name="Guardian",
            last_name="Smith"
        )
        
        # Act: Link guardian to student
        guardian.parent.add_child(student_user)
        
        # Assert: Guardian relationship is established
        assert guardian.parent.children.count() == 1
        assert student_user in guardian.parent.children.all()
        assert guardian in student_user.parents.all()
    
    def test_separated_parents_custody_scenario(self, create_parent, create_student):
        """Test separated/divorced parents with custody arrangement."""
        # Arrange: Create separated parents with different households
        parent1 = create_parent(email="parent1@home1.com", first_name="Parent1")
        parent2 = create_parent(email="parent2@home2.com", first_name="Parent2")
        child = create_student(email="child@family.com", first_name="Child")
        
        # Act: Both parents are linked (joint custody representation)
        parent1.parent.add_child(child)
        parent2.parent.add_child(child)
        
        # Assert: Both parents can access child's information
        assert child in parent1.parent.children.all()
        assert child in parent2.parent.children.all()
        assert child.parents.count() == 2
    
    def test_remove_child_from_parent(self, parent_user, student_user):
        """Test removing a child from a parent (e.g., custody change)."""
        # Arrange: Link parent and child first
        parent_user.parent.add_child(student_user)
        assert parent_user.parent.children.count() == 1
        
        # Act: Remove child from parent
        parent_user.parent.remove_child(student_user)
        
        # Assert: Child is removed
        assert parent_user.parent.children.count() == 0
        assert student_user not in parent_user.parent.children.all()
        
        # Assert: Reverse relationship also updated
        assert parent_user not in student_user.parents.all()
    
    def test_parent_with_no_children(self, parent_user):
        """Test parent with no children (e.g., newly registered parent)."""
        # Assert: Parent has no children initially
        assert parent_user.parent.children.count() == 0
        assert list(parent_user.parent.get_children_list()) == []
    
    def test_student_with_no_parents(self, student_user):
        """Test student with no parents linked (e.g., institutional placement)."""
        # Assert: Student has no parents linked
        assert student_user.parents.count() == 0
        assert list(student_user.parents.all()) == []
    
    def test_many_to_many_independence(self, create_parent, create_student):
        """Test that many-to-many relationships are independent."""
        # Arrange: Create multiple families
        parent1 = create_parent(email="parent1@test.com")
        parent2 = create_parent(email="parent2@test.com")
        student1 = create_student(email="student1@test.com")
        student2 = create_student(email="student2@test.com")
        
        # Act: Create different family structures
        parent1.parent.add_child(student1)
        parent2.parent.add_child(student2)
        
        # Assert: Relationships are independent
        assert parent1.parent.children.count() == 1
        assert parent2.parent.children.count() == 1
        assert student2 not in parent1.parent.children.all()
        assert student1 not in parent2.parent.children.all()


@pytest.mark.django_db
class TestParentViewingChildrenData:
    """
    Use Case 8: Parent Viewing Children Data
    
    Expectations:
    ✔ Returns queryset of SchoolUsers
    ✔ Parent can retrieve all their children
    ✔ Efficient data access for dashboards
    """
    
    def test_parent_get_children_list(self, family):
        """Test parent can retrieve list of their children."""
        # Arrange: Use pre-configured family fixture
        parent = family["parent"]
        expected_children = family["children"]
        
        # Act: Get children list
        children = parent.parent.get_children_list()
        
        # Assert: Returns queryset of children
        assert children.count() == 2
        assert list(children) == expected_children
        
        # Assert: Returns SchoolUser instances
        for child in children:
            assert isinstance(child, SchoolUser)
    
    def test_parent_view_multiple_children_details(self, create_parent, create_student):
        """Test parent viewing details of multiple children."""
        # Arrange: Create parent with three children
        parent = create_parent(email="parent@view.com")
        child1 = create_student(email="child1@view.com", first_name="Alice", last_name="View")
        child2 = create_student(email="child2@view.com", first_name="Bob", last_name="View")
        child3 = create_student(email="child3@view.com", first_name="Charlie", last_name="View")
        
        parent.parent.add_child(child1)
        parent.parent.add_child(child2)
        parent.parent.add_child(child3)
        
        # Act: Get children list
        children = parent.parent.get_children_list()
        
        # Assert: All children are returned
        assert children.count() == 3
        
        # Assert: Can access each child's details
        children_list = list(children)
        emails = [child.email for child in children_list]
        names = [child.get_full_name() for child in children_list]
        
        assert "child1@view.com" in emails
        assert "child2@view.com" in emails
        assert "child3@view.com" in emails
        assert "Alice View" in names
        assert "Bob View" in names
        assert "Charlie View" in names
    
    def test_parent_children_queryset_operations(self, family):
        """Test that children list supports queryset operations."""
        # Arrange: Use family fixture
        parent = family["parent"]
        
        # Act: Get children queryset
        children = parent.parent.get_children_list()
        
        # Assert: Queryset supports filtering
        assert children.filter(email__contains="child1").exists()
        
        # Assert: Queryset supports ordering
        ordered = children.order_by("first_name")
        assert ordered.count() == 2
        
        # Assert: Queryset supports count
        assert children.count() == 2
    
    def test_parent_access_child_profile_data(self, family):
        """Test parent can access child's profile data for dashboard."""
        # Arrange: Get parent and children
        parent = family["parent"]
        children = parent.parent.get_children_list()
        
        # Act: Access profile data for each child
        for child in children:
            # Assert: Can access student profile
            assert hasattr(child, "student")
            assert child.student is not None
            
            # Assert: Can access student details
            assert child.email is not None
            assert child.get_full_name() is not None
            
            # Assert: Can verify student is in correct group
            assert child.groups.filter(name=RoleEnum.STUDENT.value).exists()
    
    def test_empty_children_list_for_new_parent(self, parent_user):
        """Test that new parent with no children returns empty queryset."""
        # Act: Get children list
        children = parent_user.parent.get_children_list()
        
        # Assert: Returns empty queryset (not None)
        assert children is not None
        assert children.count() == 0
        assert list(children) == []
    
    def test_parent_children_returns_only_linked_students(self, create_parent, multiple_students):
        """Test that parent only sees their own children, not all students."""
        # Arrange: Create parent and link to only first two students
        parent = create_parent(email="parent@selective.com")
        parent.parent.add_child(multiple_students[0])
        parent.parent.add_child(multiple_students[1])
        # Note: multiple_students[2] is NOT linked
        
        # Act: Get parent's children
        children = parent.parent.get_children_list()
        
        # Assert: Only linked children are returned
        assert children.count() == 2
        assert multiple_students[0] in children
        assert multiple_students[1] in children
        assert multiple_students[2] not in children
    
    def test_multiple_parents_view_shared_child(self, create_parent, student_user):
        """Test multiple parents can independently view shared child."""
        # Arrange: Create mother and father accounts
        mother = create_parent(email="mother@shared.com", first_name="Mother")
        father = create_parent(email="father@shared.com", first_name="Father")
        
        mother.parent.add_child(student_user)
        father.parent.add_child(student_user)
        
        # Act: Both parents get their children list
        mother_children = mother.parent.get_children_list()
        father_children = father.parent.get_children_list()
        
        # Assert: Both see the same child
        assert mother_children.count() == 1
        assert father_children.count() == 1
        assert student_user in mother_children
        assert student_user in father_children
    
    def test_parent_dashboard_data_access(self, family):
        """Test realistic parent dashboard data access scenario."""
        # Arrange: Parent logs in and needs dashboard data
        parent = family["parent"]
        
        # Act: Simulate dashboard data retrieval
        children = parent.parent.get_children_list()
        
        # Assert: Can build dashboard with children's information
        dashboard_data = [
            {
                "name": child.get_full_name(),
                "email": child.email,
                "profile_type": "Student",
                "is_active": child.is_active,
            }
            for child in children
        ]
        
        assert len(dashboard_data) == 2
        assert all(item["profile_type"] == "Student" for item in dashboard_data)
        assert all(item["is_active"] is True for item in dashboard_data)
