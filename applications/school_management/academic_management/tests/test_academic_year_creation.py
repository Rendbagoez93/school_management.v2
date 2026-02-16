"""
Test Use Case 1: Creating a New Academic Year (Fresh Start)

Real-World Scenario:
Admin creates a new academic year with:
- Name → 2026 / 2027
- Start → 2026-07-01
- End → 2027-06-30
- Deployment → FRESH_START

Expectations:
✔ Valid if: start_date < end_date
✔ Status defaults to SETUP
✔ setup_completed = False
✔ Grades can be created → Allowed
✔ Student enrollments → Not yet typical

Invalid Case:
✘ Start date >= End date
✘ Expectation: Raise "Start date must be before end date."
"""

import pytest
from datetime import timedelta
from django.core.exceptions import ValidationError

from applications.school_management.academic_management.models import AcademicYear
from applications.school_management.grade_management.models import Grade


@pytest.mark.django_db
class TestFreshStartAcademicYearCreation:
    """Test creating a new academic year with fresh start deployment."""
    
    def test_create_valid_fresh_start_academic_year(self, academic_year_dates):
        """Test creating a valid fresh start academic year."""
        academic_year = AcademicYear.objects.create(
            name="2026 / 2027",
            start_date=academic_year_dates["start_date"],
            end_date=academic_year_dates["end_date"],
            deployment_type=AcademicYear.DeploymentType.FRESH_START,
        )
        
        # Verify it was created correctly
        assert academic_year.name == "2026 / 2027"
        assert academic_year.start_date == academic_year_dates["start_date"]
        assert academic_year.end_date == academic_year_dates["end_date"]
        assert academic_year.deployment_type == AcademicYear.DeploymentType.FRESH_START
        
        # Verify defaults
        assert academic_year.status == AcademicYear.Status.SETUP
        assert academic_year.setup_completed is False
        assert academic_year.is_active is True
    
    def test_start_date_must_be_before_end_date(self, base_date):
        """Test that start_date must be before end_date."""
        academic_year = AcademicYear(
            name="Invalid Year",
            start_date=base_date,
            end_date=base_date - timedelta(days=1),  # End before start!
            deployment_type=AcademicYear.DeploymentType.FRESH_START,
        )
        
        # Should raise validation error
        with pytest.raises(ValidationError) as exc_info:
            academic_year.full_clean()
        
        assert "Start date must be before end date" in str(exc_info.value)
    
    def test_start_date_equal_to_end_date_is_invalid(self, base_date):
        """Test that start_date equal to end_date is invalid."""
        academic_year = AcademicYear(
            name="Same Date Year",
            start_date=base_date,
            end_date=base_date,  # Same as start!
            deployment_type=AcademicYear.DeploymentType.FRESH_START,
        )
        
        with pytest.raises(ValidationError) as exc_info:
            academic_year.full_clean()
        
        assert "Start date must be before end date" in str(exc_info.value)
    
    def test_fresh_start_defaults_to_setup_status(self, academic_year_dates):
        """Test that fresh start academic year defaults to SETUP status."""
        academic_year = AcademicYear.objects.create(
            name="2026 / 2027 Default",
            start_date=academic_year_dates["start_date"],
            end_date=academic_year_dates["end_date"],
            deployment_type=AcademicYear.DeploymentType.FRESH_START,
        )
        
        assert academic_year.status == AcademicYear.Status.SETUP
        assert academic_year.is_in_setup is True
    
    def test_fresh_start_setup_completed_defaults_to_false(self, academic_year_dates):
        """Test that setup_completed defaults to False."""
        academic_year = AcademicYear.objects.create(
            name="2026 / 2027 Setup",
            start_date=academic_year_dates["start_date"],
            end_date=academic_year_dates["end_date"],
            deployment_type=AcademicYear.DeploymentType.FRESH_START,
        )
        
        assert academic_year.setup_completed is False
    
    def test_academic_year_name_must_be_unique(self, fresh_start_academic_year):
        """Test that academic year names must be unique."""
        # Try to create another year with same name
        with pytest.raises(Exception):  # IntegrityError
            AcademicYear.objects.create(
                name=fresh_start_academic_year.name,  # Duplicate name
                start_date=fresh_start_academic_year.start_date,
                end_date=fresh_start_academic_year.end_date,
                deployment_type=AcademicYear.DeploymentType.FRESH_START,
            )


@pytest.mark.django_db
class TestGradeCreationDuringSetup:
    """Test that grades can be created during SETUP phase."""
    
    def test_can_create_grades_during_setup(self, fresh_start_academic_year):
        """Test that grades can be created when academic year is in SETUP."""
        # Verify we're in SETUP status
        assert fresh_start_academic_year.status == AcademicYear.Status.SETUP
        assert fresh_start_academic_year.can_accept_grades() is True
        
        # Create a grade
        grade = Grade.objects.create(
            name="Class 1A",
            grade="1",
            grade_type="Primary",
            academic_year=fresh_start_academic_year,
        )
        
        assert grade.academic_year == fresh_start_academic_year
        assert grade.name == "Class 1A"
    
    def test_multiple_grades_can_be_created(self, fresh_start_academic_year):
        """Test that multiple grades can be created during setup."""
        grades_data = [
            {"name": "Class 1A", "grade": "1", "grade_type": "Primary"},
            {"name": "Class 1B", "grade": "1", "grade_type": "Primary"},
            {"name": "Class 2A", "grade": "2", "grade_type": "Primary"},
        ]
        
        for grade_data in grades_data:
            Grade.objects.create(
                academic_year=fresh_start_academic_year,
                **grade_data
            )
        
        # Verify all grades were created
        assert fresh_start_academic_year.grades.count() == 3
    
    def test_grade_creation_respects_academic_year_policy(self, fresh_start_academic_year):
        """Test that grades can only be created when policy allows."""
        # During SETUP, grades can be created
        assert Grade.can_be_created_for_year(fresh_start_academic_year) is True
        
        grade = Grade.objects.create(
            name="Test Grade",
            grade="1",
            academic_year=fresh_start_academic_year,
        )
        
        assert grade.pk is not None


@pytest.mark.django_db
class TestAcademicYearProperties:
    """Test academic year helper properties and methods."""
    
    def test_is_in_setup_property(self, fresh_start_academic_year):
        """Test is_in_setup property returns True for SETUP status."""
        assert fresh_start_academic_year.is_in_setup is True
        assert fresh_start_academic_year.status == AcademicYear.Status.SETUP
    
    def test_is_in_enrollment_property(self, fresh_start_academic_year):
        """Test is_in_enrollment property returns False for SETUP status."""
        assert fresh_start_academic_year.is_in_enrollment is False
    
    def test_is_active_year_property(self, fresh_start_academic_year):
        """Test is_active_year returns True for SETUP status."""
        # SETUP is considered an active year
        assert fresh_start_academic_year.is_active_year is True
    
    def test_can_accept_grades_during_setup(self, fresh_start_academic_year):
        """Test can_accept_grades returns True during SETUP."""
        assert fresh_start_academic_year.can_accept_grades() is True
    
    def test_string_representation(self, fresh_start_academic_year):
        """Test __str__ method returns academic year name."""
        assert str(fresh_start_academic_year) == fresh_start_academic_year.name


@pytest.mark.django_db
class TestDateValidation:
    """Test comprehensive date validation scenarios."""
    
    def test_valid_one_year_duration(self, base_date):
        """Test academic year with standard one-year duration."""
        academic_year = AcademicYear.objects.create(
            name="One Year Duration",
            start_date=base_date,
            end_date=base_date + timedelta(days=365),
            deployment_type=AcademicYear.DeploymentType.FRESH_START,
        )
        
        academic_year.full_clean()  # Should not raise
        assert academic_year.pk is not None
    
    def test_valid_short_duration(self, base_date):
        """Test academic year with shorter duration (e.g., summer term)."""
        academic_year = AcademicYear.objects.create(
            name="Short Duration",
            start_date=base_date,
            end_date=base_date + timedelta(days=90),  # 3 months
            deployment_type=AcademicYear.DeploymentType.FRESH_START,
        )
        
        academic_year.full_clean()  # Should not raise
        assert academic_year.pk is not None
    
    def test_invalid_negative_duration(self, base_date):
        """Test that negative duration (end before start) is invalid."""
        academic_year = AcademicYear(
            name="Negative Duration",
            start_date=base_date,
            end_date=base_date - timedelta(days=100),
            deployment_type=AcademicYear.DeploymentType.FRESH_START,
        )
        
        with pytest.raises(ValidationError) as exc_info:
            academic_year.full_clean()
        
        assert "Start date must be before end date" in str(exc_info.value)
    
    def test_minimum_one_day_duration(self, base_date):
        """Test that at least one day duration is required."""
        academic_year = AcademicYear.objects.create(
            name="One Day Duration",
            start_date=base_date,
            end_date=base_date + timedelta(days=1),
            deployment_type=AcademicYear.DeploymentType.FRESH_START,
        )
        
        academic_year.full_clean()  # Should not raise
        assert academic_year.pk is not None


@pytest.mark.django_db
class TestDeploymentTypeDefaults:
    """Test deployment type defaults and behavior."""
    
    def test_deployment_type_defaults_to_fresh_start(self, academic_year_dates):
        """Test that deployment_type defaults to FRESH_START."""
        academic_year = AcademicYear.objects.create(
            name="Default Deployment",
            start_date=academic_year_dates["start_date"],
            end_date=academic_year_dates["end_date"],
            # Not specifying deployment_type
        )
        
        assert academic_year.deployment_type == AcademicYear.DeploymentType.FRESH_START
    
    def test_can_explicitly_set_fresh_start(self, academic_year_dates):
        """Test explicitly setting FRESH_START deployment type."""
        academic_year = AcademicYear.objects.create(
            name="Explicit Fresh Start",
            start_date=academic_year_dates["start_date"],
            end_date=academic_year_dates["end_date"],
            deployment_type=AcademicYear.DeploymentType.FRESH_START,
        )
        
        assert academic_year.deployment_type == AcademicYear.DeploymentType.FRESH_START
