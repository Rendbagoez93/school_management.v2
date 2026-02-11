"""Django app configuration for user management."""

from django.apps import AppConfig


class UserManagementConfig(AppConfig):
    """Configuration for the user management application."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "applications.user_management"
    verbose_name = "User Management"

    def ready(self):
        """Import signal handlers when app is ready."""
        # Import signal handlers here if needed in the future
        # Example: from . import signals
        pass

