"""Staff-related data transfer objects (DTOs)."""

from pydantic import BaseModel


class StaffMetrics(BaseModel):
    """Metrics for staff members in the school management system."""

    total_staff: int = 0
    teaching_staff: int = 0
    non_teaching_staff: int = 0
