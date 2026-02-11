"""Django admin configuration for user management models."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from applications.user_management.models import Parent, SchoolStaff, SchoolUser, Student


@admin.register(SchoolUser)
class SchoolUserAdmin(BaseUserAdmin):
    """Admin interface for SchoolUser model."""

    list_display = ("username", "email", "first_name", "last_name", "is_staff", "get_roles")
    list_filter = ("is_staff", "is_superuser", "is_active", "groups")
    search_fields = ("username", "first_name", "last_name", "email")
    ordering = ("username",)

    def get_roles(self, obj):
        """Display user roles."""
        return ", ".join(obj.groups.values_list("name", flat=True))

    get_roles.short_description = "Roles"


@admin.register(Parent)
class ParentAdmin(admin.ModelAdmin):
    """Admin interface for Parent model."""

    list_display = ("user", "get_user_email", "created_at", "updated_at")
    search_fields = ("user__username", "user__email", "user__first_name", "user__last_name")
    list_filter = ("created_at", "updated_at")
    filter_horizontal = ("children",)
    readonly_fields = ("created_at", "updated_at")

    def get_user_email(self, obj):
        """Display user email."""
        return obj.user.email

    get_user_email.short_description = "Email"


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    """Admin interface for Student model."""

    list_display = ("user", "get_user_email", "created_at", "updated_at")
    search_fields = ("user__username", "user__email", "user__first_name", "user__last_name")
    list_filter = ("created_at", "updated_at")
    readonly_fields = ("created_at", "updated_at")

    def get_user_email(self, obj):
        """Display user email."""
        return obj.user.email

    get_user_email.short_description = "Email"


@admin.register(SchoolStaff)
class SchoolStaffAdmin(admin.ModelAdmin):
    """Admin interface for SchoolStaff model."""

    list_display = ("user", "get_user_email", "get_staff_role", "created_at", "updated_at")
    search_fields = ("user__username", "user__email", "user__first_name", "user__last_name")
    list_filter = ("created_at", "updated_at", "user__groups")
    readonly_fields = ("created_at", "updated_at")

    def get_user_email(self, obj):
        """Display user email."""
        return obj.user.email

    get_user_email.short_description = "Email"

    def get_staff_role(self, obj):
        """Display staff role."""
        return ", ".join(obj.user.groups.values_list("name", flat=True))

    get_staff_role.short_description = "Role"

