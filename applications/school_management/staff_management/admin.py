from django.contrib import admin

from .models import StaffMember, Teacher


@admin.register(StaffMember)
class StaffMemberAdmin(admin.ModelAdmin):
	list_display = ("employee_id", "user", "department", "job_title", "is_active")
	search_fields = ("employee_id", "user__email", "user__first_name", "user__last_name")
	list_filter = ("department", "is_active")


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
	list_display = ("employee_id", "user", "department", "specialization", "is_active")
	search_fields = ("employee_id", "user__email", "user__first_name", "user__last_name")
	list_filter = ("department", "is_active")
