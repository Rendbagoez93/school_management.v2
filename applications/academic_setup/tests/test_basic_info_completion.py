"""
Test Scenario 2: Admin Completes Basic Info

Real-World Expectations:
✔ basic_info_completed = True
✔ current_step should advance to next step
"""

import pytest
from applications.academic_setup.models import AcademicYearSetup
from applications.academic_setup.orchestrator import AcademicYearOrchestrator


@pytest.mark.django_db
class TestBasicInfoCompletion:
    """Test basic info completion step."""
    
    def test_mark_basic_info_complete(self, fresh_start_academic_year):
        """Verify marking basic info as complete updates the setup."""
        # Initially not completed
        setup = fresh_start_academic_year.setup_progress
        assert setup.basic_info_completed is False
        assert setup.current_step == AcademicYearSetup.SetupSteps.BASIC_INFO
        
        # Mark basic info as complete
        AcademicYearOrchestrator.mark_step_complete(
            fresh_start_academic_year,
            AcademicYearSetup.SetupSteps.BASIC_INFO,
        )
        
        # Refresh and verify
        setup.refresh_from_db()
        assert setup.basic_info_completed is True
    
    def test_current_step_advances_after_basic_info(self, fresh_start_academic_year):
        """Verify current_step advances to IMPORT_GRADES after basic info."""
        setup = fresh_start_academic_year.setup_progress
        
        # Mark basic info as complete
        AcademicYearOrchestrator.mark_step_complete(
            fresh_start_academic_year,
            AcademicYearSetup.SetupSteps.BASIC_INFO,
        )
        
        # Verify step advanced
        setup.refresh_from_db()
        assert setup.current_step == AcademicYearSetup.SetupSteps.IMPORT_GRADES
    
    def test_completion_percentage_increases(self, fresh_start_academic_year):
        """Verify completion percentage increases after basic info."""
        # Initially 0%
        initial_percentage = AcademicYearOrchestrator.get_completion_percentage(
            fresh_start_academic_year
        )
        assert initial_percentage == 0.0
        
        # Complete basic info
        AcademicYearOrchestrator.mark_step_complete(
            fresh_start_academic_year,
            AcademicYearSetup.SetupSteps.BASIC_INFO,
        )
        
        # Percentage should increase (1/5 steps = 20%)
        new_percentage = AcademicYearOrchestrator.get_completion_percentage(
            fresh_start_academic_year
        )
        assert new_percentage == 20.0
    
    def test_setup_still_not_complete_after_basic_info(self, fresh_start_academic_year):
        """Verify setup is not complete after just basic info."""
        AcademicYearOrchestrator.mark_step_complete(
            fresh_start_academic_year,
            AcademicYearSetup.SetupSteps.BASIC_INFO,
        )
        
        setup = fresh_start_academic_year.setup_progress
        setup.refresh_from_db()
        
        assert setup.is_complete() is False
        assert AcademicYearOrchestrator.is_setup_complete(fresh_start_academic_year) is False
    
    def test_other_steps_remain_incomplete(self, fresh_start_academic_year):
        """Verify other steps remain incomplete after basic info."""
        AcademicYearOrchestrator.mark_step_complete(
            fresh_start_academic_year,
            AcademicYearSetup.SetupSteps.BASIC_INFO,
        )
        
        setup = fresh_start_academic_year.setup_progress
        setup.refresh_from_db()
        
        # Only basic info should be completed
        assert setup.basic_info_completed is True
        assert setup.import_grades_completed is False
        assert setup.import_students_completed is False
        assert setup.assign_classrooms_completed is False
        assert setup.review_completed is False


@pytest.mark.django_db
class TestBasicInfoCompletionFixture:
    """Test using the basic_info_completed_setup fixture."""
    
    def test_fixture_has_basic_info_completed(self, basic_info_completed_setup):
        """Verify fixture provides setup with basic info completed."""
        assert basic_info_completed_setup.basic_info_completed is True
    
    def test_fixture_current_step_is_import_grades(self, basic_info_completed_setup):
        """Verify fixture has current step as IMPORT_GRADES."""
        assert basic_info_completed_setup.current_step == AcademicYearSetup.SetupSteps.IMPORT_GRADES
    
    def test_fixture_other_steps_incomplete(self, basic_info_completed_setup):
        """Verify fixture has other steps incomplete."""
        assert basic_info_completed_setup.import_grades_completed is False
        assert basic_info_completed_setup.import_students_completed is False
        assert basic_info_completed_setup.assign_classrooms_completed is False
        assert basic_info_completed_setup.review_completed is False


@pytest.mark.django_db
class TestSequentialStepCompletion:
    """Test completing steps in sequence."""
    
    def test_completing_steps_sequentially_advances_current_step(self, fresh_start_academic_year):
        """Verify completing each step advances current_step."""
        setup = fresh_start_academic_year.setup_progress
        
        # Step 1: BASIC_INFO
        assert setup.current_step == AcademicYearSetup.SetupSteps.BASIC_INFO
        AcademicYearOrchestrator.mark_step_complete(
            fresh_start_academic_year,
            AcademicYearSetup.SetupSteps.BASIC_INFO,
        )
        setup.refresh_from_db()
        assert setup.current_step == AcademicYearSetup.SetupSteps.IMPORT_GRADES
        
        # Step 2: IMPORT_GRADES
        AcademicYearOrchestrator.mark_step_complete(
            fresh_start_academic_year,
            AcademicYearSetup.SetupSteps.IMPORT_GRADES,
            import_method=AcademicYearSetup.ImportMethod.CSV,
        )
        setup.refresh_from_db()
        assert setup.current_step == AcademicYearSetup.SetupSteps.IMPORT_STUDENTS
        
        # Step 3: IMPORT_STUDENTS
        AcademicYearOrchestrator.mark_step_complete(
            fresh_start_academic_year,
            AcademicYearSetup.SetupSteps.IMPORT_STUDENTS,
            import_method=AcademicYearSetup.ImportMethod.CSV,
        )
        setup.refresh_from_db()
        assert setup.current_step == AcademicYearSetup.SetupSteps.ASSIGN_CLASSROOMS
        
        # Step 4: ASSIGN_CLASSROOMS
        AcademicYearOrchestrator.mark_step_complete(
            fresh_start_academic_year,
            AcademicYearSetup.SetupSteps.ASSIGN_CLASSROOMS,
            import_method=AcademicYearSetup.ImportMethod.MANUAL,
        )
        setup.refresh_from_db()
        assert setup.current_step == AcademicYearSetup.SetupSteps.REVIEW
        
        # Step 5: REVIEW
        AcademicYearOrchestrator.mark_step_complete(
            fresh_start_academic_year,
            AcademicYearSetup.SetupSteps.REVIEW,
        )
        setup.refresh_from_db()
        assert setup.current_step == AcademicYearSetup.SetupSteps.COMPLETED
    
    def test_completion_percentage_increases_with_each_step(self, fresh_start_academic_year):
        """Verify completion percentage increases with each step."""
        percentages = []
        
        # Initial
        percentages.append(
            AcademicYearOrchestrator.get_completion_percentage(fresh_start_academic_year)
        )
        
        # Complete each step
        steps = [
            (AcademicYearSetup.SetupSteps.BASIC_INFO, None),
            (AcademicYearSetup.SetupSteps.IMPORT_GRADES, AcademicYearSetup.ImportMethod.CSV),
            (AcademicYearSetup.SetupSteps.IMPORT_STUDENTS, AcademicYearSetup.ImportMethod.CSV),
            (AcademicYearSetup.SetupSteps.ASSIGN_CLASSROOMS, AcademicYearSetup.ImportMethod.MANUAL),
            (AcademicYearSetup.SetupSteps.REVIEW, None),
        ]
        
        for step, method in steps:
            AcademicYearOrchestrator.mark_step_complete(
                fresh_start_academic_year,
                step,
                import_method=method,
            )
            percentages.append(
                AcademicYearOrchestrator.get_completion_percentage(fresh_start_academic_year)
            )
        
        # Verify percentages increase
        assert percentages == [0.0, 20.0, 40.0, 60.0, 80.0, 100.0]


@pytest.mark.django_db
class TestImportMethodRequirement:
    """Test that import steps require import_method."""
    
    def test_import_grades_step_sets_import_method(self, fresh_start_academic_year):
        """Verify import_method is set when completing IMPORT_GRADES."""
        AcademicYearOrchestrator.mark_step_complete(
            fresh_start_academic_year,
            AcademicYearSetup.SetupSteps.BASIC_INFO,
        )
        
        AcademicYearOrchestrator.mark_step_complete(
            fresh_start_academic_year,
            AcademicYearSetup.SetupSteps.IMPORT_GRADES,
            import_method=AcademicYearSetup.ImportMethod.CSV,
        )
        
        setup = fresh_start_academic_year.setup_progress
        setup.refresh_from_db()
        
        assert setup.grades_import_method == AcademicYearSetup.ImportMethod.CSV
        assert setup.import_grades_completed is True
    
    def test_import_students_step_sets_import_method(self, grades_imported_setup):
        """Verify import_method is set when completing IMPORT_STUDENTS."""
        academic_year = grades_imported_setup.academic_year
        
        AcademicYearOrchestrator.mark_step_complete(
            academic_year,
            AcademicYearSetup.SetupSteps.IMPORT_STUDENTS,
            import_method=AcademicYearSetup.ImportMethod.CSV,
        )
        
        grades_imported_setup.refresh_from_db()
        
        assert grades_imported_setup.students_import_method == AcademicYearSetup.ImportMethod.CSV
        assert grades_imported_setup.import_students_completed is True
    
    def test_different_import_methods_can_be_used(self, fresh_start_academic_year):
        """Verify different import methods can be used for different steps."""
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
            import_method=AcademicYearSetup.ImportMethod.API,
        )
        
        orchestrator.mark_step_complete(
            fresh_start_academic_year,
            AcademicYearSetup.SetupSteps.ASSIGN_CLASSROOMS,
            import_method=AcademicYearSetup.ImportMethod.MANUAL,
        )
        
        setup = fresh_start_academic_year.setup_progress
        setup.refresh_from_db()
        
        # Verify different methods
        assert setup.grades_import_method == AcademicYearSetup.ImportMethod.CSV
        assert setup.students_import_method == AcademicYearSetup.ImportMethod.API
        assert setup.classrooms_import_method == AcademicYearSetup.ImportMethod.MANUAL
