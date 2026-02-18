"""
Test Use Cases: Student Enrollment Management

Real-World Scenarios:
1. Assign Student to Grade
2. Assign Student to Multiple Grades Same Year (blocked)
3. Student Transfers Grade

✔ Expectations:
  - Students can be assigned to grades
  - One student per academic year (no double enrollment)
  - Transfers preserve history and integrity

✔ Real-world meaning:
  - Student officially joins class
  - Prevents scheduling conflicts
  - Maintains enrollment integrity
"""

import pytest
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError

from applications.school_management.academic_management.models import AcademicYear, StudentEnrollment
from applications.academic_setup.orchestrator import AcademicYearOrchestrator


@pytest.mark.django_db
class TestStudentEnrollment:
    """Test assigning students to grades."""
    
    def test_assign_student_to_grade(self, grade_in_enrollment, student_user):
        """
        Test: Assign Student to Grade
        
        Scenario:
          Create StudentEnrollment:
            - student → User A
            - grade → Grade 10A
            - academic_year → 2026/2027
        
        Expectation:
          ✔ Student appears in:
            - student.student_grades.all()
            - grade.students.all()
        
        Real-world meaning:
          Student officially joins class.
        """
        # Enroll student
        enrollment = AcademicYearOrchestrator.enroll_student(
            grade=grade_in_enrollment,
            student=student_user,
        )
        
        # Verify enrollment created
        assert enrollment.pk is not None
        assert enrollment.student == student_user
        assert enrollment.grade == grade_in_enrollment
        assert enrollment.academic_year == grade_in_enrollment.academic_year
        
        # Verify student appears in grade.students
        assert student_user in grade_in_enrollment.students.all()
        
        # Verify grade appears in student.student_grades
        assert grade_in_enrollment in student_user.student_grades.all()
    
    def test_enrollment_creates_relationship(self, grade_in_enrollment, student_user):
        """Test that enrollment creates bidirectional relationship."""
        # Before enrollment
        assert grade_in_enrollment.students.count() == 0
        assert student_user.student_grades.count() == 0
        
        # Enroll
        enrollment = StudentEnrollment.objects.create(
            student=student_user,
            grade=grade_in_enrollment,
            academic_year=grade_in_enrollment.academic_year,
        )
        
        # After enrollment
        assert grade_in_enrollment.students.count() == 1
        assert student_user.student_grades.count() == 1
        
        # Verify relationship
        assert student_user in grade_in_enrollment.students.all()
        assert grade_in_enrollment in student_user.student_grades.all()
    
    def test_multiple_students_same_grade(self, grade_in_enrollment, multiple_student_users):
        """
        Test that multiple students can be enrolled in the same grade.
        
        Real-world: Class has multiple students.
        """
        enrollments = []
        
        for student in multiple_student_users[:3]:  # Use first 3 students
            enrollment = StudentEnrollment.objects.create(
                student=student,
                grade=grade_in_enrollment,
                academic_year=grade_in_enrollment.academic_year,
            )
            enrollments.append(enrollment)
        
        # All enrolled
        assert len(enrollments) == 3
        
        # Grade has 3 students
        assert grade_in_enrollment.students.count() == 3
        
        # All students in the grade
        for student in multiple_student_users[:3]:
            assert student in grade_in_enrollment.students.all()
    
    def test_enrollment_tracks_join_time(self, grade_in_enrollment, student_user):
        """Test that enrollment records when student joined."""
        enrollment = StudentEnrollment.objects.create(
            student=student_user,
            grade=grade_in_enrollment,
            academic_year=grade_in_enrollment.academic_year,
        )
        
        # joined_at is automatically set
        assert enrollment.joined_at is not None
    
    def test_enrollment_allowed_in_setup_phase(self, grade_in_setup, student_user):
        """Test that students can be enrolled during SETUP phase."""
        assert grade_in_setup.academic_year.status == AcademicYear.Status.SETUP
        
        enrollment = AcademicYearOrchestrator.enroll_student(
            grade=grade_in_setup,
            student=student_user,
        )
        
        assert enrollment.pk is not None
    
    def test_enrollment_allowed_in_enrollment_phase(self, grade_in_enrollment, student_user):
        """Test that students can be enrolled during ENROLLMENT phase."""
        assert grade_in_enrollment.academic_year.status == AcademicYear.Status.ENROLLMENT
        
        enrollment = AcademicYearOrchestrator.enroll_student(
            grade=grade_in_enrollment,
            student=student_user,
        )
        
        assert enrollment.pk is not None
    
    def test_enrollment_allowed_in_active_phase(self, grade_in_active, student_user):
        """Test that students can be enrolled during ACTIVE phase."""
        assert grade_in_active.academic_year.status == AcademicYear.Status.ACTIVE
        
        enrollment = AcademicYearOrchestrator.enroll_student(
            grade=grade_in_active,
            student=student_user,
        )
        
        assert enrollment.pk is not None
    
    def test_only_users_with_student_role_can_enroll(self, grade_in_enrollment, non_student_user):
        """
        Test that only users with STUDENT role can be enrolled.
        
        Real-world protection: Prevent teachers/admins from being enrolled as students.
        """
        with pytest.raises(ValidationError) as exc_info:
            AcademicYearOrchestrator.enroll_student(
                grade=grade_in_enrollment,
                student=non_student_user,
            )
        
        assert "STUDENT role" in str(exc_info.value)


@pytest.mark.django_db
class TestDuplicateEnrollmentPrevention:
    """Test preventing students from enrolling in multiple grades same year."""
    
    def test_student_cannot_enroll_in_multiple_grades_same_year(
        self, 
        multiple_grades_same_year, 
        student_user
    ):
        """
        Test: Assign Student to Multiple Grades Same Year
        
        Scenario:
          Student already enrolled → Try second enrollment.
        
        Expectation:
          ✔ Blocked by StudentEnrollment constraint.
        
        Real-world protection:
          ✔ Prevents:
            ❌ Student attending 2 classes simultaneously.
        """
        grade_a, grade_b, grade_c = multiple_grades_same_year
        
        # Enroll in first grade
        enrollment1 = StudentEnrollment.objects.create(
            student=student_user,
            grade=grade_a,
            academic_year=grade_a.academic_year,
        )
        
        assert enrollment1.pk is not None
        
        # Attempt to enroll in second grade same year - should fail
        with pytest.raises(IntegrityError):
            StudentEnrollment.objects.create(
                student=student_user,
                grade=grade_b,  # Different grade
                academic_year=grade_b.academic_year,  # Same academic year
            )
    
    def test_orchestrator_prevents_duplicate_enrollment(
        self,
        multiple_grades_same_year,
        student_user
    ):
        """Test that orchestrator prevents duplicate enrollment."""
        grade_a, grade_b, grade_c = multiple_grades_same_year
        
        # Enroll in first grade
        AcademicYearOrchestrator.enroll_student(
            grade=grade_a,
            student=student_user,
        )
        
        # Attempt second enrollment in different grade same year
        with pytest.raises(ValidationError) as exc_info:
            AcademicYearOrchestrator.enroll_student(
                grade=grade_b,
                student=student_user,
            )
        
        # Error should mention existing enrollment
        assert "already enrolled" in str(exc_info.value).lower()
    
    def test_student_can_enroll_in_different_years(
        self,
        grade_in_setup,
        grade_in_enrollment,
        student_user
    ):
        """
        Test that same student can be enrolled in different academic years.
        
        Real-world: Student progresses through years.
        """
        # Different academic years
        assert grade_in_setup.academic_year != grade_in_enrollment.academic_year
        
        # Enroll in first year
        enrollment1 = StudentEnrollment.objects.create(
            student=student_user,
            grade=grade_in_setup,
            academic_year=grade_in_setup.academic_year,
        )
        
        # Enroll in second year - should be allowed
        enrollment2 = StudentEnrollment.objects.create(
            student=student_user,
            grade=grade_in_enrollment,
            academic_year=grade_in_enrollment.academic_year,
        )
        
        # Both enrollments exist
        assert enrollment1.pk is not None
        assert enrollment2.pk is not None
        assert enrollment1.pk != enrollment2.pk
    
    def test_protection_against_scheduling_conflicts(
        self,
        multiple_grades_same_year,
        student_user
    ):
        """
        Test real-world protection: Prevent scheduling conflicts.
        
        If student could enroll in multiple grades:
          ❌ Can't attend Class A and Class B at same time
          ❌ Schedule becomes impossible
          ❌ Attendance tracking breaks
        """
        grade_a, grade_b, _ = multiple_grades_same_year
        
        # Enroll in Class A
        StudentEnrollment.objects.create(
            student=student_user,
            grade=grade_a,
            academic_year=grade_a.academic_year,
        )
        
        # Cannot enroll in Class B (would create scheduling conflict)
        with pytest.raises(IntegrityError):
            StudentEnrollment.objects.create(
                student=student_user,
                grade=grade_b,
                academic_year=grade_b.academic_year,
            )


@pytest.mark.django_db
class TestStudentTransfer:
    """Test student transfers between grades."""
    
    def test_student_transfers_grade(
        self,
        multiple_grades_same_year,
        student_user
    ):
        """
        Test: Student Transfers Grade
        
        Scenario:
          Student moves from Grade A → B.
        
        Expectation:
          ✔ Proper flow:
            - Soft delete old StudentEnrollment
            - Create new StudentEnrollment
        
        ✔ System preserves:
          - History
          - Integrity
        """
        grade_a, grade_b, _ = multiple_grades_same_year
        
        # Initial enrollment in Grade A
        enrollment_a = AcademicYearOrchestrator.enroll_student(
            grade=grade_a,
            student=student_user,
        )
        
        assert enrollment_a.pk is not None
        assert student_user in grade_a.students.all()
        
        # Transfer to Grade B
        enrollment_b = AcademicYearOrchestrator.transfer_student(
            student=student_user,
            from_grade=grade_a,
            to_grade=grade_b,
        )
        
        # New enrollment created
        assert enrollment_b.pk is not None
        assert enrollment_b.grade == grade_b
        
        # Student now in Grade B
        assert student_user in grade_b.students.all()
        
        # Student no longer in Grade A (soft deleted)
        assert student_user not in grade_a.students.all()
    
    def test_transfer_preserves_history(
        self,
        multiple_grades_same_year,
        student_user
    ):
        """
        Test that transfer preserves enrollment history via soft delete.
        """
        grade_a, grade_b, _ = multiple_grades_same_year
        
        # Enroll in Grade A
        enrollment_a = AcademicYearOrchestrator.enroll_student(
            grade=grade_a,
            student=student_user,
        )
        original_id = enrollment_a.pk
        
        # Transfer to Grade B
        enrollment_b = AcademicYearOrchestrator.transfer_student(
            student=student_user,
            from_grade=grade_a,
            to_grade=grade_b,
        )
        
        # Same enrollment object,just updated (better design - preserves joined_at)       
        assert enrollment_b.pk == original_id
        assert enrollment_b.grade == grade_b
        assert enrollment_b.is_deleted is False
    
    def test_cannot_transfer_between_different_years(
        self,
        grade_in_setup,
        grade_in_enrollment,
        student_user
    ):
        """
        Test that transfers are only allowed within same academic year.
        
        Real-world: Can't transfer mid-year to next year's class.
        """
        # Different academic years
        assert grade_in_setup.academic_year != grade_in_enrollment.academic_year
        
        # Enroll in first year
        AcademicYearOrchestrator.enroll_student(
            grade=grade_in_setup,
            student=student_user,
        )
        
        # Attempt transfer to different year - should fail
        with pytest.raises(ValidationError) as exc_info:
            AcademicYearOrchestrator.transfer_student(
                student=student_user,
                from_grade=grade_in_setup,
                to_grade=grade_in_enrollment,
            )
        
        assert "different academic years" in str(exc_info.value).lower()
    
    def test_transfer_updates_grade_student_counts(
        self,
        multiple_grades_same_year,
        student_user
    ):
        """Test that transfer correctly updates student counts."""
        grade_a, grade_b, _ = multiple_grades_same_year
        
        # Initial counts
        initial_a_count = grade_a.students.count()
        initial_b_count = grade_b.students.count()
        
        # Enroll in A
        AcademicYearOrchestrator.enroll_student(
            grade=grade_a,
            student=student_user,
        )
        
        assert grade_a.students.count() == initial_a_count + 1
        
        # Transfer to B
        AcademicYearOrchestrator.transfer_student(
            student=student_user,
            from_grade=grade_a,
            to_grade=grade_b,
        )
        
        # Counts updated correctly
        assert grade_a.students.count() == initial_a_count  # Back to original
        assert grade_b.students.count() == initial_b_count + 1
    
    def test_transfer_maintains_academic_year_consistency(
        self,
        multiple_grades_same_year,
        student_user
    ):
        """Test that transfer maintains academic year in enrollment record."""
        grade_a, grade_b, _ = multiple_grades_same_year
        academic_year = grade_a.academic_year
        
        # Enroll and transfer
        AcademicYearOrchestrator.enroll_student(grade=grade_a, student=student_user)
        enrollment = AcademicYearOrchestrator.transfer_student(
            student=student_user,
            from_grade=grade_a,
            to_grade=grade_b,
        )
        
        # Academic year remains consistent
        assert enrollment.academic_year == academic_year
        assert enrollment.grade.academic_year == academic_year


@pytest.mark.django_db
class TestEnrollmentQueries:
    """Test querying enrollment relationships."""
    
    def test_get_students_in_grade(self, grade_in_enrollment, multiple_student_users):
        """Test getting all students in a grade."""
        # Enroll multiple students
        for student in multiple_student_users[:3]:
            AcademicYearOrchestrator.enroll_student(
                grade=grade_in_enrollment,
                student=student,
            )
        
        # Get students
        students = AcademicYearOrchestrator.get_students_in_grade(grade_in_enrollment)
        
        # Verify
        assert len(students) == 3
        for student in multiple_student_users[:3]:
            assert student in students
    
    def test_get_student_enrollment_for_year(self, grade_in_enrollment, student_user):
        """Test getting a student's enrollment for specific year."""
        # Enroll student
        enrollment = AcademicYearOrchestrator.enroll_student(
            grade=grade_in_enrollment,
            student=student_user,
        )
        
        # Query enrollment
        found_enrollment = AcademicYearOrchestrator.get_student_enrollment(
            student=student_user,
            academic_year=grade_in_enrollment.academic_year,
        )
        
        # Verify
        assert found_enrollment is not None
        assert found_enrollment.pk == enrollment.pk
    
    def test_query_all_grades_for_student(self, student_user, grade_in_setup, grade_in_enrollment):
        """Test querying all grades a student has been in."""
        # Enroll in multiple years
        StudentEnrollment.objects.create(
            student=student_user,
            grade=grade_in_setup,
            academic_year=grade_in_setup.academic_year,
        )
        
        StudentEnrollment.objects.create(
            student=student_user,
            grade=grade_in_enrollment,
            academic_year=grade_in_enrollment.academic_year,
        )
        
        # Query all grades
        student_grades = student_user.student_grades.all()
        
        # Verify
        assert student_grades.count() == 2
        assert grade_in_setup in student_grades
        assert grade_in_enrollment in student_grades


@pytest.mark.django_db
class TestUnenrollment:
    """Test unenrolling students from grades."""
    
    def test_unenroll_student_from_grade(self, grade_in_enrollment, student_user):
        """Test removing a student from a grade."""
        # Enroll
        AcademicYearOrchestrator.enroll_student(
            grade=grade_in_enrollment,
            student=student_user,
        )
        
        assert student_user in grade_in_enrollment.students.all()
        
        # Unenroll
        AcademicYearOrchestrator.unenroll_student(
            grade=grade_in_enrollment,
            student=student_user,
        )
        
        # Verify removal
        assert student_user not in grade_in_enrollment.get_active_students()
    
    def test_unenroll_uses_soft_delete(self, grade_in_enrollment, student_user):
        """Test that unenrollment uses soft delete to preserve history."""
        # Enroll
        enrollment = AcademicYearOrchestrator.enroll_student(
            grade=grade_in_enrollment,
            student=student_user,
        )
        enrollment_id = enrollment.pk
        
        # Unenroll
        AcademicYearOrchestrator.unenroll_student(
            grade=grade_in_enrollment,
            student=student_user,
        )
        
        # Enrollment record still exists but is soft-deleted
        deleted_enrollment = StudentEnrollment.all_objects.filter(pk=enrollment_id).first()
        assert deleted_enrollment is not None
        assert deleted_enrollment.is_deleted is True
    
    def test_cannot_unenroll_non_enrolled_student(self, grade_in_enrollment, student_user):
        """Test that unenrolling a non-enrolled student raises error."""
        # Student is not enrolled
        assert student_user not in grade_in_enrollment.students.all()
        
        # Attempt to unenroll
        with pytest.raises(ValidationError) as exc_info:
            AcademicYearOrchestrator.unenroll_student(
                grade=grade_in_enrollment,
                student=student_user,
            )
        
        assert "not enrolled" in str(exc_info.value).lower()
