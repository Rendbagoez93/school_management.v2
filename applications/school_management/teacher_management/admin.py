from django.contrib import admin

from .models import Teacher


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
	list_display = ("employee_id", "user", "department", "specialization", "is_active", "date_of_joining")
	search_fields = ("employee_id", "user__email", "user__first_name", "user__last_name", "department")
	list_filter = ("department", "is_active", "date_of_joining")
	readonly_fields = ("date_joined", "date_modified")
	ordering = ("employee_id",)
