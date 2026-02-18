"""
Test Scenario 1: New Academic Year Created

Real-World Expectations:
- Setup auto starts at BASIC_INFO
- No imports done
- System locked from operational use
"""

import pytest
from applications.school_management.academic_management.models import AcademicYear
from applications.academic_setup.models import AcademicYearSetup, ImportTask
from applications.academic_setup.orchestrator import AcademicYearOrchestrator


@pytest.mark.django_db
class TestNewAcademicYearCreation:
    """Test that new academic years are created with correct initial state."""
    
    def test_new_academic_year_has_setup_status(self, fresh_start_academic_year):
        """Verify new academic year starts in SETUP status."""
        assert fresh_start_academic_year.status == AcademicYear.Status.SETUP
        assert fresh_start_academic_year.setup_completed is False
    
    def test_new_academic_year_is_not_active_for_operations(self, fresh_start_academic_year):
        """Verify system is locked from operational use during setup."""
        # Academic year should not be marked as ready for operations
        assert fresh_start_academic_year.status != AcademicYear.Status.ACTIVE
        assert fresh_start_academic_year.setup_completed is False
        
        # Setup must be incomplete
        assert not AcademicYearOrchestrator.is_setup_complete(fresh_start_academic_year)
    
    def test_setup_progress_created_automatically(self, fresh_start_academic_year):
        """Verify setup progress tracker is created automatically."""
        # Setup progress should exist
        assert hasattr(fresh_start_academic_year, 'setup_progress')
        setup = fresh_start_academic_year.setup_progress
        
        # Verify it's an AcademicYearSetup instance
        assert isinstance(setup, AcademicYearSetup)
        assert setup.academic_year == fresh_start_academic_year
    
    def test_setup_auto_starts_at_basic_info(self, fresh_start_academic_year):
        """Verify setup automatically starts at BASIC_INFO step."""
        setup = fresh_start_academic_year.setup_progress
        assert setup.current_step == AcademicYearSetup.SetupSteps.BASIC_INFO
    
    def test_no_steps_completed_initially(self, fresh_start_academic_year):
        """Verify no setup steps are completed initially."""
        setup = fresh_start_academic_year.setup_progress
        
        assert setup.basic_info_completed is False
        assert setup.import_grades_completed is False
        assert setup.import_students_completed is False
        assert setup.assign_classrooms_completed is False
        assert setup.review_completed is False
    
    def test_no_imports_done_initially(self, fresh_start_academic_year):
        """Verify no import methods are set initially."""
        setup = fresh_start_academic_year.setup_progress
        
        assert setup.grades_import_method == AcademicYearSetup.ImportMethod.NONE
        assert setup.students_import_method == AcademicYearSetup.ImportMethod.NONE
        assert setup.classrooms_import_method == AcademicYearSetup.ImportMethod.NONE
    
    def test_no_import_tasks_exist_initially(self, fresh_start_academic_year):
        """Verify no import tasks exist for new academic year."""
        import_tasks = ImportTask.objects.filter(
            academic_year=fresh_start_academic_year
        )
        assert import_tasks.count() == 0
    
    def test_setup_is_not_complete(self, fresh_start_academic_year):
        """Verify setup is not complete initially."""
        setup = fresh_start_academic_year.setup_progress
        
        assert setup.is_complete() is False
        assert setup.is_ready() is False
        assert AcademicYearOrchestrator.is_setup_complete(fresh_start_academic_year) is False
    
    def test_completion_percentage_is_zero(self, fresh_start_academic_year):
        """Verify setup completion percentage is 0%."""
        percentage = AcademicYearOrchestrator.get_completion_percentage(
            fresh_start_academic_year
        )
        assert percentage == 0.0


@pytest.mark.django_db
class TestMidYearAcademicYearCreation:
    """Test mid-year academic year creation."""
    
    def test_mid_year_academic_year_setup_status(self, mid_year_academic_year):
        """Verify mid-year academic year starts in SETUP status."""
        assert mid_year_academic_year.status == AcademicYear.Status.SETUP
        assert mid_year_academic_year.deployment_type == AcademicYear.DeploymentType.MID_YEAR
    
    def test_mid_year_has_setup_progress(self, mid_year_academic_year):
        """Verify mid-year academic year has setup progress."""
        assert hasattr(mid_year_academic_year, 'setup_progress')
        setup = mid_year_academic_year.setup_progress
        assert setup.current_step == AcademicYearSetup.SetupSteps.BASIC_INFO
    
    def test_mid_year_no_enrollment_dates_required(self, mid_year_academic_year):
        """Verify mid-year doesn't require enrollment dates."""
        # Mid-year can have null enrollment dates
        assert mid_year_academic_year.enrollment_start_date is None
        assert mid_year_academic_year.enrollment_end_date is None


@pytest.mark.django_db
class TestSystemLockedDuringSetup:
    """Test that system operations are locked during setup."""
    
    def test_cannot_transition_to_enrollment_without_setup(self, fresh_start_academic_year):
        """Verify cannot transition to ENROLLMENT before setup is complete."""
        with pytest.raises(Exception):  # Should raise ValidationError
            AcademicYearOrchestrator.transition_to_enrollment(fresh_start_academic_year)
    
    def test_cannot_transition_to_active_without_setup_fresh_start(self, fresh_start_academic_year):
        """Verify fresh start cannot transition to ACTIVE without going through ENROLLMENT."""
        with pytest.raises(Exception):  # Should raise ValidationError
            AcademicYearOrchestrator.transition_to_active(fresh_start_academic_year)
    
    def test_academic_year_not_accessible_for_operations(self, fresh_start_academic_year):
        """Verify academic year is not in operational state."""
        # Should not be active
        assert fresh_start_academic_year.status != AcademicYear.Status.ACTIVE
        
        # Should not be in enrollment
        assert fresh_start_academic_year.status != AcademicYear.Status.ENROLLMENT
        
        # Should be in setup only
        assert fresh_start_academic_year.status == AcademicYear.Status.SETUP


@pytest.mark.django_db
class TestAcademicYearCreationEdgeCases:
    """Test edge cases in academic year creation."""
    
    def test_cannot_create_duplicate_academic_year_name(self, fresh_start_academic_year, academic_year_dates):
        """Verify cannot create academic year with duplicate name."""
        with pytest.raises(Exception):  # IntegrityError due to unique constraint
            AcademicYearOrchestrator.create_academic_year(
                name=fresh_start_academic_year.name,  # Same name
                start_date=academic_year_dates["start_date"],
                end_date=academic_year_dates["end_date"],
                deployment_type=AcademicYear.DeploymentType.FRESH_START,
            )
    
    def test_multiple_academic_years_can_exist_in_setup(self, fresh_start_academic_year, academic_year_dates):
        """Verify multiple academic years can be in SETUP simultaneously."""
        # Create another academic year
        another_year = AcademicYearOrchestrator.create_academic_year(
            name="2027-2028",
            start_date=academic_year_dates["start_date"],
            end_date=academic_year_dates["end_date"],
            deployment_type=AcademicYear.DeploymentType.FRESH_START,
        )
        
        # Both should be in SETUP
        assert fresh_start_academic_year.status == AcademicYear.Status.SETUP
        assert another_year.status == AcademicYear.Status.SETUP
    
    def test_setup_progress_one_to_one_relationship(self, fresh_start_academic_year):
        """Verify setup progress has one-to-one relationship with academic year."""
        setup = fresh_start_academic_year.setup_progress
        
        # Attempting to create another setup for same year should fail
        with pytest.raises(Exception):  # IntegrityError
            AcademicYearSetup.objects.create(
                academic_year=fresh_start_academic_year,
                current_step=AcademicYearSetup.SetupSteps.BASIC_INFO,
            )
    
    def test_orchestrator_creates_both_year_and_setup_atomically(self, academic_year_dates):
        """Verify orchestrator creates both academic year and setup in single transaction."""
        year = AcademicYearOrchestrator.create_academic_year(
            name="2028-2029",
            start_date=academic_year_dates["start_date"],
            end_date=academic_year_dates["end_date"],
            deployment_type=AcademicYear.DeploymentType.FRESH_START,
        )
        
        # Both should exist immediately
        assert year.id is not None
        assert hasattr(year, 'setup_progress')
        assert year.setup_progress.id is not None
        
        # They should be linked
        assert year.setup_progress.academic_year == year
