"""Data Transfer Objects (DTOs) for user management.

This module contains Pydantic models used for data validation
and transfer between layers.
"""

from applications.user_management.pojo.staff import StaffMetrics

__all__ = ["StaffMetrics"]
