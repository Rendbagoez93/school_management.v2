"""
Test Scenario 5: Setup Completion Gate

Real-World Expectation:
System should enforce:
✔ AcademicYear can only be ACTIVE if setup is ready
✔ All required steps must be completed
✔ Cannot skip steps
✔ Proper transitions enforced
"""

import pytest
from django.core.exceptions import ValidationError

from applications.school_management.academic_management.models import AcademicYear
from applications.academic_setup.models import AcademicYearSetup
from applications.academic_setup.orchestrator import AcademicYearOrchestrator


@pytest.mark.django_db
class TestSetupCompletionRequirements:
    """Test that setup must be complete before transitioning."""
    
    def test_cannot_activate_without_complete_setup(self, fresh_start_academic_year):
        """Verify cannot transition to ACTIVE without completing setup."""
        # Fresh start should go through ENROLLMENT first
        with pytest.raises(ValidationError):
            AcademicYearOrchestrator.transition_to_active(fresh_start_academic_year)
    
    def test_cannot_transition_to_enrollment_without_setup(self, fresh_start_academic_year):
        """Verify cannot transition to ENROLLMENT without complete setup."""
        with pytest.raises(ValidationError) as exc_info:
            AcademicYearOrchestrator.transition_to_enrollment(fresh_start_academic_year)
        
        assert "setup must be complete" in str(exc_info.value).lower()
    
    def test_setup_is_complete_returns_false_when_incomplete(self, fresh_start_academic_year):
        """Verify is_setup_complete returns False when incomplete."""
        assert AcademicYearOrchestrator.is_setup_complete(fresh_start_academic_year) is False
    
    def test_setup_is_complete_returns_true_when_all_steps_done(self, fully_completed_setup):
        """Verify is_setup_complete returns True when all steps completed."""
        academic_year = fully_completed_setup.academic_year
        assert AcademicYearOrchestrator.is_setup_complete(academic_year) is True


@pytest.mark.django_db
class TestAllStepsRequiredForCompletion:
    """Test that all steps must be completed."""
    
    def test_missing_basic_info_prevents_completion(self, fresh_start_academic_year):
        """Verify missing basic info prevents setup completion."""
        orchestrator = AcademicYearOrchestrator
        setup = fresh_start_academic_year.setup_progress
        
        # Mark all steps except basic_info as completed (artificially)
        setup.import_grades_completed = True
        setup.import_students_completed = True
        setup.assign_classrooms_completed = True
        setup.review_completed = True
        setup.grades_import_method = AcademicYearSetup.ImportMethod.CSV
        setup.students_import_method = AcademicYearSetup.ImportMethod.CSV
        setup.classrooms_import_method = AcademicYearSetup.ImportMethod.MANUAL
        setup.save()
        
        # Setup should not be complete
        assert setup.is_complete() is False
        assert orchestrator.is_setup_complete(fresh_start_academic_year) is False
    
    def test_missing_grades_import_prevents_completion(self, fresh_start_academic_year):
        """Verify missing grades import prevents completion."""
        setup = fresh_start_academic_year.setup_progress
        
        # Mark all except grades import
        setup.basic_info_completed = True
        setup.import_students_completed = True
        setup.assign_classrooms_completed = True
        setup.review_completed = True
        setup.students_import_method = AcademicYearSetup.ImportMethod.CSV
        setup.classrooms_import_method = AcademicYearSetup.ImportMethod.MANUAL
        setup.save()
        
        assert setup.is_complete() is False
    
    def test_missing_students_import_prevents_completion(self, fresh_start_academic_year):
        """Verify missing students import prevents completion."""
        setup = fresh_start_academic_year.setup_progress
        
        # Mark all except students import
        setup.basic_info_completed = True
        setup.import_grades_completed = True
        setup.assign_classrooms_completed = True
        setup.review_completed = True
        setup.grades_import_method = AcademicYearSetup.ImportMethod.CSV
        setup.classrooms_import_method = AcademicYearSetup.ImportMethod.MANUAL
        setup.save()
        
        assert setup.is_complete() is False
    
    def test_missing_classrooms_assignment_prevents_completion(self, fresh_start_academic_year):
        """Verify missing classroom assignment prevents completion."""
        setup = fresh_start_academic_year.setup_progress
        
        # Mark all except classrooms
        setup.basic_info_completed = True
        setup.import_grades_completed = True
        setup.import_students_completed = True
        setup.review_completed = True
        setup.grades_import_method = AcademicYearSetup.ImportMethod.CSV
        setup.students_import_method = AcademicYearSetup.ImportMethod.CSV
        setup.save()
        
        assert setup.is_complete() is False
    
    def test_missing_review_prevents_completion(self, fresh_start_academic_year):
        """Verify missing review prevents completion."""
        setup = fresh_start_academic_year.setup_progress
        
        # Mark all except review
        setup.basic_info_completed = True
        setup.import_grades_completed = True
        setup.import_students_completed = True
        setup.assign_classrooms_completed = True
        setup.grades_import_method = AcademicYearSetup.ImportMethod.CSV
        setup.students_import_method = AcademicYearSetup.ImportMethod.CSV
        setup.classrooms_import_method = AcademicYearSetup.ImportMethod.MANUAL
        setup.save()
        
        assert setup.is_complete() is False
    
    def test_all_steps_completed_marks_setup_complete(self, fully_completed_setup):
        """Verify all steps completed marks setup as complete."""
        assert fully_completed_setup.basic_info_completed is True
        assert fully_completed_setup.import_grades_completed is True
        assert fully_completed_setup.import_students_completed is True
        assert fully_completed_setup.assign_classrooms_completed is True
        assert fully_completed_setup.review_completed is True
        assert fully_completed_setup.is_complete() is True


@pytest.mark.django_db
class TestFreshStartTransitionGate:
    """Test fresh start academic year transitions."""
    
    def test_fresh_start_requires_enrollment_phase(self, fresh_start_academic_year):
        """Verify fresh start must go through ENROLLMENT phase."""
        # Complete all setup steps
        orchestrator = AcademicYearOrchestrator
        orchestrator.mark_step_complete(
            fresh_start_academic_year,
            AcademicYearSetup.SetupSteps.BASIC_INFO,
        )
        orchestrator.mark_step_complete(
            fresh_start_academic_year,
            AcademicYearSetup.SetupSteps.IMPORT_GRADES,
            import_method=AcademicYearSetup.ImportMethod.CSV,
        )
        orchestrator.mark_step_complete(
            fresh_start_academic_year,
            AcademicYearSetup.SetupSteps.IMPORT_STUDENTS,
            import_method=AcademicYearSetup.ImportMethod.CSV,
        )
        orchestrator.mark_step_complete(
            fresh_start_academic_year,
            AcademicYearSetup.SetupSteps.ASSIGN_CLASSROOMS,
            import_method=AcademicYearSetup.ImportMethod.MANUAL,
        )
        orchestrator.mark_step_complete(
            fresh_start_academic_year,
            AcademicYearSetup.SetupSteps.REVIEW,
        )
        
        # Should be able to transition to ENROLLMENT
        orchestrator.transition_to_enrollment(fresh_start_academic_year)
        
        fresh_start_academic_year.refresh_from_db()
        assert fresh_start_academic_year.status == AcademicYear.Status.ENROLLMENT
        assert fresh_start_academic_year.setup_completed is True
    
    def test_fresh_start_can_go_from_enrollment_to_active(self, fresh_start_academic_year):
        """Verify fresh start can transition from ENROLLMENT to ACTIVE."""
        # Complete setup and move to enrollment
        orchestrator = AcademicYearOrchestrator
        self._complete_all_setup_steps(fresh_start_academic_year, orchestrator)
        orchestrator.transition_to_enrollment(fresh_start_academic_year)
        
        # Now transition to ACTIVE
        orchestrator.transition_to_active(fresh_start_academic_year)
        
        fresh_start_academic_year.refresh_from_db()
        assert fresh_start_academic_year.status == AcademicYear.Status.ACTIVE
    
    def _complete_all_setup_steps(self, academic_year, orchestrator):
        """Helper to complete all setup steps."""
        orchestrator.mark_step_complete(
            academic_year,
            AcademicYearSetup.SetupSteps.BASIC_INFO,
        )
        orchestrator.mark_step_complete(
            academic_year,
            AcademicYearSetup.SetupSteps.IMPORT_GRADES,
            import_method=AcademicYearSetup.ImportMethod.CSV,
        )
        orchestrator.mark_step_complete(
            academic_year,
            AcademicYearSetup.SetupSteps.IMPORT_STUDENTS,
            import_method=AcademicYearSetup.ImportMethod.CSV,
        )
        orchestrator.mark_step_complete(
            academic_year,
            AcademicYearSetup.SetupSteps.ASSIGN_CLASSROOMS,
            import_method=AcademicYearSetup.ImportMethod.MANUAL,
        )
        orchestrator.mark_step_complete(
            academic_year,
            AcademicYearSetup.SetupSteps.REVIEW,
        )


@pytest.mark.django_db
class TestMidYearTransitionGate:
    """Test mid-year academic year transitions."""
    
    def test_mid_year_cannot_have_enrollment_phase(self, mid_year_academic_year):
        """Verify mid-year cannot transition to ENROLLMENT."""
        # Complete all setup steps
        orchestrator = AcademicYearOrchestrator
        self._complete_all_setup_steps(mid_year_academic_year, orchestrator)
        
        # Should not be able to transition to ENROLLMENT
        with pytest.raises(ValidationError) as exc_info:
            orchestrator.transition_to_enrollment(mid_year_academic_year)
        
        assert "mid-year" in str(exc_info.value).lower()
    
    def test_mid_year_goes_directly_to_active(self, mid_year_academic_year):
        """Verify mid-year can go directly from SETUP to ACTIVE."""
        # Complete all setup steps
        orchestrator = AcademicYearOrchestrator
        self._complete_all_setup_steps(mid_year_academic_year, orchestrator)
        
        # Should be able to go directly to ACTIVE
        orchestrator.transition_to_active(mid_year_academic_year)
        
        mid_year_academic_year.refresh_from_db()
        assert mid_year_academic_year.status == AcademicYear.Status.ACTIVE
        assert mid_year_academic_year.setup_completed is True
    
    def _complete_all_setup_steps(self, academic_year, orchestrator):
        """Helper to complete all setup steps."""
        orchestrator.mark_step_complete(
            academic_year,
            AcademicYearSetup.SetupSteps.BASIC_INFO,
        )
        orchestrator.mark_step_complete(
            academic_year,
            AcademicYearSetup.SetupSteps.IMPORT_GRADES,
            import_method=AcademicYearSetup.ImportMethod.CSV,
        )
        orchestrator.mark_step_complete(
            academic_year,
            AcademicYearSetup.SetupSteps.IMPORT_STUDENTS,
            import_method=AcademicYearSetup.ImportMethod.CSV,
        )
        orchestrator.mark_step_complete(
            academic_year,
            AcademicYearSetup.SetupSteps.ASSIGN_CLASSROOMS,
            import_method=AcademicYearSetup.ImportMethod.MANUAL,
        )
        orchestrator.mark_step_complete(
            academic_year,
            AcademicYearSetup.SetupSteps.REVIEW,
        )


@pytest.mark.django_db
class TestActiveAcademicYearGate:
    """Test that only properly setup years can be active."""
    
    def test_active_academic_year_fixture_is_ready(self, active_academic_year):
        """Verify active_academic_year fixture is properly set up."""
        assert active_academic_year.status == AcademicYear.Status.ACTIVE
        assert active_academic_year.setup_completed is True
        assert AcademicYearOrchestrator.is_setup_complete(active_academic_year) is True
    
    def test_active_academic_year_has_completed_setup(self, active_academic_year):
        """Verify active academic year has all setup steps completed."""
        setup = active_academic_year.setup_progress
        
        assert setup.basic_info_completed is True
        assert setup.import_grades_completed is True
        assert setup.import_students_completed is True
        assert setup.assign_classrooms_completed is True
        assert setup.review_completed is True
        assert setup.current_step == AcademicYearSetup.SetupSteps.COMPLETED
    
    def test_completion_percentage_is_100_for_active(self, active_academic_year):
        """Verify completion percentage is 100% for active year."""
        percentage = AcademicYearOrchestrator.get_completion_percentage(active_academic_year)
        assert percentage == 100.0


@pytest.mark.django_db
class TestSetupProgressTracking:
    """Test setup progress percentage tracking."""
    
    def test_completion_percentage_at_each_step(self, fresh_start_academic_year):
        """Verify completion percentage at each step."""
        orchestrator = AcademicYearOrchestrator
        
        # 0%
        assert orchestrator.get_completion_percentage(fresh_start_academic_year) == 0.0
        
        # 20% after basic info
        orchestrator.mark_step_complete(
            fresh_start_academic_year,
            AcademicYearSetup.SetupSteps.BASIC_INFO,
        )
        assert orchestrator.get_completion_percentage(fresh_start_academic_year) == 20.0
        
        # 40% after grades import
        orchestrator.mark_step_complete(
            fresh_start_academic_year,
            AcademicYearSetup.SetupSteps.IMPORT_GRADES,
            import_method=AcademicYearSetup.ImportMethod.CSV,
        )
        assert orchestrator.get_completion_percentage(fresh_start_academic_year) == 40.0
        
        # 60% after students import
        orchestrator.mark_step_complete(
            fresh_start_academic_year,
            AcademicYearSetup.SetupSteps.IMPORT_STUDENTS,
            import_method=AcademicYearSetup.ImportMethod.CSV,
        )
        assert orchestrator.get_completion_percentage(fresh_start_academic_year) == 60.0
        
        # 80% after classrooms
        orchestrator.mark_step_complete(
            fresh_start_academic_year,
            AcademicYearSetup.SetupSteps.ASSIGN_CLASSROOMS,
            import_method=AcademicYearSetup.ImportMethod.MANUAL,
        )
        assert orchestrator.get_completion_percentage(fresh_start_academic_year) == 80.0
        
        # 100% after review
        orchestrator.mark_step_complete(
            fresh_start_academic_year,
            AcademicYearSetup.SetupSteps.REVIEW,
        )
        assert orchestrator.get_completion_percentage(fresh_start_academic_year) == 100.0
