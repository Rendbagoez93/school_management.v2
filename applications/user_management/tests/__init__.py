"""Repository layer for user management.

This module contains read and write operations following the
repository pattern for separation of concerns.
"""

from applications.user_management.repo.read import get_staff_metrics
from applications.user_management.repo.write import (
    create_principal_user,
    create_staff_user,
)

__all__ = [
    "get_staff_metrics",
    "create_principal_user",
    "create_staff_user",
]
