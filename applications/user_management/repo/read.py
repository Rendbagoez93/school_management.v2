"""Read operations for user management."""

from applications.user_management.models import SchoolUser
from applications.user_management.pojo.staff import StaffMetrics


def get_staff_metrics() -> StaffMetrics:
    """Retrieve metrics for staff members in the school management system."""
    all_staff = SchoolUser.objects.all()
    all_staff_count: int = all_staff.count()
    teaching_staff: int = SchoolUser.objects.get_teachers().count()
    non_teaching_staff: int = all_staff_count - teaching_staff

    return StaffMetrics(
        total_staff=all_staff_count,
        teaching_staff=teaching_staff,
        non_teaching_staff=non_teaching_staff,
    )
