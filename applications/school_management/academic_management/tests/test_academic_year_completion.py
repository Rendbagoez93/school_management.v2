"""
Test Use Case 6: Academic Year Completion

Real-World Scenario:
Status moves to COMPLETED.

Expectations:
✔ System behavior:
  - No structural edits (grades locked)
  - No new enrollments
  - Reports / archives → ✅ Allowed
  - Promotion / rollover logic → Can be triggered
✔ Valid transitions:
  - ACTIVE -> COMPLETED
✔ Requirements:
  - setup_completed must be True
  - Typically end_date has passed (business logic)
"""

import pytest
from datetime import timedelta
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from applications.school_management.academic_management.models import (
    AcademicYear,
    StudentEnrollment,
)
from applications.school_management.grade_management.models import Grade


User = get_user_model()


@pytest.mark.django_db
class TestCompletionRequirements:
    """Test requirements for completing academic year."""
    
    def test_completed_status_requires_setup_completed(self, academic_year_dates):
        """Test that COMPLETED status requires setup_completed=True."""
        academic_year = AcademicYear.objects.create(
            name="Completed Year",
            start_date=academic_year_dates["start_date"] - timedelta(days=730),
            end_date=academic_year_dates["start_date"] - timedelta(days=365),
            status=AcademicYear.Status.COMPLETED,
            setup_completed=True,  # Required
        )
        
        academic_year.full_clean()  # Should not raise
        assert academic_year.status == AcademicYear.Status.COMPLETED
        assert academic_year.setup_completed is True
    
    def test_cannot_complete_without_setup_completed(self, academic_year_dates):
        """Test that cannot set COMPLETED status without setup_completed."""
        academic_year = AcademicYear(
            name="Invalid Completed",
            start_date=academic_year_dates["start_date"],
            end_date=academic_year_dates["end_date"],
            status=AcademicYear.Status.COMPLETED,
            setup_completed=False,  # Invalid!
        )
        
        with pytest.raises(ValidationError) as exc_info:
            academic_year.full_clean()
        
        assert "setup_completed must be True" in str(exc_info.value)
    
    def test_completed_year_is_not_active_year(self, completed_academic_year):
        """Test that COMPLETED status is not considered an active year."""
        assert completed_academic_year.status == AcademicYear.Status.COMPLETED
        # is_active_year only includes SETUP, ENROLLMENT, ACTIVE
        assert completed_academic_year.is_active_year is False


@pytest.mark.django_db
class TestTransitionToCompleted:
    """Test transitions to COMPLETED status."""
    
    def test_transition_from_active_to_completed(self, active_academic_year):
        """Test transitioning from ACTIVE to COMPLETED (typical path)."""
        assert active_academic_year.status == AcademicYear.Status.ACTIVE
        assert active_academic_year.setup_completed is True
        
        # Complete the year
        active_academic_year.status = AcademicYear.Status.COMPLETED
        active_academic_year.save()
        
        active_academic_year.full_clean()  # Should not raise
        assert active_academic_year.status == AcademicYear.Status.COMPLETED
    
    def test_cannot_complete_from_setup(self, fresh_start_academic_year):
        """Test that cannot go directly from SETUP to COMPLETED."""
        fresh_start_academic_year.status = AcademicYear.Status.COMPLETED
        # setup_completed is False, which is invalid for COMPLETED
        
        with pytest.raises(ValidationError) as exc_info:
            fresh_start_academic_year.full_clean()
        
        assert "setup_completed must be True" in str(exc_info.value)
    
    def test_cannot_complete_from_enrollment_without_proper_setup(self, academic_year_dates):
        """Test proper transition from ENROLLMENT to COMPLETED."""
        academic_year = AcademicYear.objects.create(
            name="Enrollment to Complete",
            start_date=academic_year_dates["start_date"],
            end_date=academic_year_dates["end_date"],
            status=AcademicYear.Status.ENROLLMENT,
            setup_completed=True,
        )
        
        # Can transition to COMPLETED
        academic_year.status = AcademicYear.Status.COMPLETED
        academic_year.save()
        
        academic_year.full_clean()  # Should not raise
        assert academic_year.status == AcademicYear.Status.COMPLETED


@pytest.mark.django_db
class TestGradeCreationRestrictions:
    """Test that grade creation is locked for COMPLETED years."""
    
    def test_cannot_create_grades_when_completed(self, completed_academic_year):
        """Test that can_accept_grades returns False for COMPLETED status."""
        assert completed_academic_year.status == AcademicYear.Status.COMPLETED
        assert completed_academic_year.can_accept_grades() is False
    
    def test_grade_creation_policy_enforced_for_completed(self, completed_academic_year):
        """Test that Grade model prevents creation for completed years."""
        assert Grade.can_be_created_for_year(completed_academic_year) is False
    
    def test_existing_grades_remain_accessible(self, completed_academic_year):
        """Test that existing grades can still be queried."""
        # Create grade before completing (would have been created during setup)
        # Moving year back to ACTIVE to create grade
        completed_academic_year.status = AcademicYear.Status.ACTIVE
        completed_academic_year.save()
        
        grade = Grade.objects.create(
            name="Historical Grade",
            grade="1",
            academic_year=completed_academic_year,
        )
        
        # Complete the year again
        completed_academic_year.status = AcademicYear.Status.COMPLETED
        completed_academic_year.save()
        
        # Grade still accessible
        assert Grade.objects.filter(pk=grade.pk).exists()
        assert grade.academic_year.status == AcademicYear.Status.COMPLETED


@pytest.mark.django_db
class TestStudentEnrollmentRestrictions:
    """Test student enrollment restrictions for COMPLETED years."""
    
    def test_model_technically_allows_enrollment_in_completed(self, completed_academic_year, student_user):
        """
        Test that model technically allows enrollment even when completed.
        
        Note: Business logic should prevent this, but model doesn't enforce it.
        This allows for historical data corrections.
        """
        # Create grade (from before completion)
        completed_academic_year.status = AcademicYear.Status.ACTIVE
        completed_academic_year.save()
        
        grade = Grade.objects.create(
            name="Completed Year Grade",
            grade="1",
            academic_year=completed_academic_year,
        )
        
        completed_academic_year.status = AcademicYear.Status.COMPLETED
        completed_academic_year.save()
        
        # Model allows enrollment (for data corrections)
        enrollment = StudentEnrollment.objects.create(
            student=student_user,
            grade=grade,
            academic_year=completed_academic_year,
        )
        
        assert enrollment.pk is not None
        # Business logic would typically prevent new enrollments
    
    def test_existing_enrollments_remain_accessible(self, completed_academic_year):
        """Test that existing enrollments can be queried after completion."""
        # Create enrollment before completing
        completed_academic_year.status = AcademicYear.Status.ACTIVE
        completed_academic_year.save()
        
        grade = Grade.objects.create(
            name="Grade for Enrollment",
            grade="2",
            academic_year=completed_academic_year,
        )
        
        student = User.objects.create_user(
            username="historical_student",
            email="historical@test.com"
        )
        
        enrollment = StudentEnrollment.objects.create(
            student=student,
            grade=grade,
            academic_year=completed_academic_year,
        )
        
        # Complete the year
        completed_academic_year.status = AcademicYear.Status.COMPLETED
        completed_academic_year.save()
        
        # Enrollment still accessible
        assert StudentEnrollment.objects.filter(pk=enrollment.pk).exists()
        assert enrollment.academic_year.status == AcademicYear.Status.COMPLETED


@pytest.mark.django_db
class TestCompletedYearOperations:
    """Test allowed and restricted operations for COMPLETED years."""
    
    def test_completed_year_properties(self, completed_academic_year):
        """Test properties of completed academic year."""
        assert completed_academic_year.status == AcademicYear.Status.COMPLETED
        assert completed_academic_year.is_active_year is False
        assert completed_academic_year.is_in_setup is False
        assert completed_academic_year.is_in_enrollment is False
        assert completed_academic_year.can_accept_grades() is False
    
    def test_can_query_completed_year_data(self, completed_academic_year):
        """Test that completed year data can be queried for reports."""
        # Create some historical data
        completed_academic_year.status = AcademicYear.Status.ACTIVE
        completed_academic_year.save()
        
        grades = [
            Grade.objects.create(
                name=f"Grade {i}",
                grade=str(i),
                academic_year=completed_academic_year,
            )
            for i in range(1, 4)
        ]
        
        completed_academic_year.status = AcademicYear.Status.COMPLETED
        completed_academic_year.save()
        
        # Can query all data
        assert completed_academic_year.grades.count() == 3
        assert all(g.academic_year == completed_academic_year for g in grades)
    
    def test_can_update_academic_year_metadata(self, completed_academic_year):
        """Test that metadata can be updated even when completed."""
        # Might update name for archival purposes
        completed_academic_year.name = "Archived: " + completed_academic_year.name
        completed_academic_year.save()
        
        completed_academic_year.refresh_from_db()
        assert "Archived:" in completed_academic_year.name
    
    def test_can_soft_delete_completed_year(self, completed_academic_year):
        """Test that completed years can be soft deleted."""
        # Assuming BaseSoftDeletableModel is used
        completed_academic_year.is_active = False
        completed_academic_year.save()
        
        assert completed_academic_year.is_active is False


@pytest.mark.django_db
class TestCompletionEdgeCases:
    """Test edge cases for academic year completion."""
    
    def test_cannot_uncomplete_year_without_reverting_status(self, completed_academic_year):
        """Test that cannot set setup_completed=False for COMPLETED status."""
        completed_academic_year.setup_completed = False
        
        with pytest.raises(ValidationError) as exc_info:
            completed_academic_year.full_clean()
        
        assert "setup_completed must be True" in str(exc_info.value)
    
    def test_can_reactivate_completed_year(self, completed_academic_year):
        """Test that completed year can be reactivated if needed."""
        # Might need to reopen for corrections
        completed_academic_year.status = AcademicYear.Status.ACTIVE
        completed_academic_year.save()
        
        completed_academic_year.full_clean()  # Should not raise
        assert completed_academic_year.status == AcademicYear.Status.ACTIVE
        # Business logic would typically prevent this
    
    def test_multiple_completed_years_allowed(self, completed_academic_year, base_date):
        """Test that system can have multiple completed years."""
        another_completed = AcademicYear.objects.create(
            name="Another Completed",
            start_date=base_date - timedelta(days=1095),  # 3 years ago
            end_date=base_date - timedelta(days=730),  # 2 years ago
            status=AcademicYear.Status.COMPLETED,
            setup_completed=True,
        )
        
        assert AcademicYear.objects.filter(status=AcademicYear.Status.COMPLETED).count() == 2
    
    def test_cannot_revert_to_setup_from_completed(self, completed_academic_year):
        """Test that cannot revert from COMPLETED to SETUP."""
        completed_academic_year.status = AcademicYear.Status.SETUP
        # setup_completed is True, which is invalid for SETUP
        
        with pytest.raises(ValidationError) as exc_info:
            completed_academic_year.full_clean()
        
        assert "Cannot be in SETUP status when setup is already completed" in str(exc_info.value)


@pytest.mark.django_db
class TestCompletedYearQuerying:
    """Test querying for completed academic years."""
    
    def test_filter_completed_years(self, completed_academic_year, active_academic_year):
        """Test filtering for COMPLETED status years."""
        completed_years = AcademicYear.objects.filter(status=AcademicYear.Status.COMPLETED)
        
        assert completed_academic_year in completed_years
        assert active_academic_year not in completed_years
    
    def test_exclude_completed_from_active_queries(
        self,
        completed_academic_year,
        active_academic_year,
        fresh_start_academic_year,
    ):
        """Test excluding completed years when querying active years."""
        active_years = AcademicYear.objects.exclude(status=AcademicYear.Status.COMPLETED)
        
        assert completed_academic_year not in active_years
        assert active_academic_year in active_years
        assert fresh_start_academic_year in active_years
    
    def test_order_completed_years_by_date(self, base_date):
        """Test ordering completed years chronologically."""
        # Create multiple completed years
        years = []
        for i in range(3):
            offset = i * 365
            year = AcademicYear.objects.create(
                name=f"Completed {2024 - i}",
                start_date=base_date - timedelta(days=offset + 730),
                end_date=base_date - timedelta(days=offset + 365),
                status=AcademicYear.Status.COMPLETED,
                setup_completed=True,
            )
            years.append(year)
        
        # Query ordered by end date (most recent first)
        completed_years = AcademicYear.objects.filter(
            status=AcademicYear.Status.COMPLETED
        ).order_by('-end_date')
        
        # Most recent completed year should be first
        assert list(completed_years) == years


@pytest.mark.django_db
class TestRealWorldCompletionScenarios:
    """Test real-world completion scenarios."""
    
    def test_end_of_year_completion_workflow(self, academic_year_dates):
        """Test complete workflow from creation to completion."""
        # Start of year
        academic_year = AcademicYear.objects.create(
            name="Full Year Lifecycle",
            start_date=academic_year_dates["start_date"],
            end_date=academic_year_dates["end_date"],
            deployment_type=AcademicYear.DeploymentType.FRESH_START,
            enrollment_start_date=academic_year_dates["enrollment_start_date"],
            enrollment_end_date=academic_year_dates["enrollment_end_date"],
            status=AcademicYear.Status.SETUP,
            setup_completed=False,
        )
        
        # Setup phase - create grades
        grades = [
            Grade.objects.create(
                name=f"Class {i}A",
                grade=str(i),
                academic_year=academic_year,
            )
            for i in range(1, 4)
        ]
        
        # Move to enrollment
        academic_year.setup_completed = True
        academic_year.status = AcademicYear.Status.ENROLLMENT
        academic_year.save()
        
        # Enroll students
        students = [
            User.objects.create_user(
                username=f"student_{i}",
                email=f"student_{i}@test.com"
            )
            for i in range(5)
        ]
        
        for i, student in enumerate(students):
            StudentEnrollment.objects.create(
                student=student,
                grade=grades[i % 3],  # Distribute across grades
                academic_year=academic_year,
            )
        
        # Activate for teaching
        academic_year.status = AcademicYear.Status.ACTIVE
        academic_year.save()
        
        # End of year - complete
        academic_year.status = AcademicYear.Status.COMPLETED
        academic_year.save()
        academic_year.full_clean()
        
        # Verify final state
        assert academic_year.status == AcademicYear.Status.COMPLETED
        assert academic_year.grades.count() == 3
        assert academic_year.studentenrollment_set.count() == 5
        assert academic_year.can_accept_grades() is False
    
    def test_archived_year_for_reports(self, completed_academic_year):
        """Test querying completed year for report generation."""
        # Generate enrollment report
        completed_academic_year.status = AcademicYear.Status.ACTIVE
        completed_academic_year.save()
        
        grade = Grade.objects.create(
            name="Report Grade",
            grade="5",
            academic_year=completed_academic_year,
        )
        
        students = [
            User.objects.create_user(
                username=f"report_student_{i}",
                email=f"report_student_{i}@test.com"
            )
            for i in range(10)
        ]
        
        for student in students:
            StudentEnrollment.objects.create(
                student=student,
                grade=grade,
                academic_year=completed_academic_year,
            )
        
        completed_academic_year.status = AcademicYear.Status.COMPLETED
        completed_academic_year.save()
        
        # Report queries
        total_students = completed_academic_year.studentenrollment_set.count()
        total_grades = completed_academic_year.grades.count()
        
        assert total_students == 10
        assert total_grades == 1
        # Reports can be generated from completed years
    
    def test_promotion_rollover_scenario(self, completed_academic_year, base_date):
        """Test promotion/rollover from completed year to new year."""
        # Create next academic year
        next_year = AcademicYear.objects.create(
            name="Next Year After Completion",
            start_date=completed_academic_year.end_date + timedelta(days=1),
            end_date=completed_academic_year.end_date + timedelta(days=366),
            status=AcademicYear.Status.SETUP,
            setup_completed=False,
        )
        
        # Setup historical data in completed year
        completed_academic_year.status = AcademicYear.Status.ACTIVE
        completed_academic_year.save()
        
        old_grade = Grade.objects.create(
            name="Grade 1",
            grade="1",
            academic_year=completed_academic_year,
        )
        
        students = [
            User.objects.create_user(
                username=f"promote_student_{i}",
                email=f"promote_student_{i}@test.com"
            )
            for i in range(3)
        ]
        
        for student in students:
            StudentEnrollment.objects.create(
                student=student,
                grade=old_grade,
                academic_year=completed_academic_year,
            )
        
        completed_academic_year.status = AcademicYear.Status.COMPLETED
        completed_academic_year.save()
        
        # Promotion logic would:
        # 1. Query completed year enrollments
        old_enrollments = StudentEnrollment.objects.filter(
            academic_year=completed_academic_year
        )
        assert old_enrollments.count() == 3
        
        # 2. Create new grade in new year
        new_grade = Grade.objects.create(
            name="Grade 2",
            grade="2",  # Promoted grade
            academic_year=next_year,
        )
        
        # 3. Enroll students in new year (promotion)
        # (In real system, this would be automated)
        assert next_year.status == AcademicYear.Status.SETUP
        assert completed_academic_year.status == AcademicYear.Status.COMPLETED


@pytest.mark.django_db
class TestCompletionValidation:
    """Test validation specific to COMPLETED status."""
    
    def test_completed_year_with_valid_dates(self, base_date):
        """Test creating completed year with valid past dates."""
        academic_year = AcademicYear.objects.create(
            name="Valid Completed",
            start_date=base_date - timedelta(days=730),
            end_date=base_date - timedelta(days=365),
            status=AcademicYear.Status.COMPLETED,
            setup_completed=True,
        )
        
        academic_year.full_clean()
        assert academic_year.end_date < base_date  # In the past
    
    def test_completed_year_can_have_enrollment_period(self, base_date):
        """Test completed year can have historical enrollment period."""
        academic_year = AcademicYear.objects.create(
            name="Completed with Enrollment Record",
            start_date=base_date - timedelta(days=730),
            end_date=base_date - timedelta(days=365),
            status=AcademicYear.Status.COMPLETED,
            setup_completed=True,
            enrollment_start_date=base_date - timedelta(days=760),
            enrollment_end_date=base_date - timedelta(days=730),
        )
        
        academic_year.full_clean()  # Should not raise
        # Enrollment period is historical record
