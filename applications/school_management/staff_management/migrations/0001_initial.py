# Generated manually to implement staff management domain models.

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="StaffMember",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("date_joined", models.DateTimeField(auto_now_add=True, verbose_name="Date Joined")),
                ("date_modified", models.DateTimeField(auto_now=True, verbose_name="Date Modified")),
                ("is_deleted", models.BooleanField(default=False, verbose_name="Is Deleted")),
                ("deleted_at", models.DateTimeField(blank=True, null=True, verbose_name="Deleted At")),
                ("employee_id", models.CharField(db_index=True, max_length=32, unique=True)),
                ("department", models.CharField(blank=True, max_length=100)),
                ("job_title", models.CharField(blank=True, max_length=100)),
                ("date_of_joining", models.DateField(blank=True, null=True)),
                ("is_active", models.BooleanField(default=True)),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="staff_member_profile",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["employee_id"],
                "indexes": [
                    models.Index(fields=["department"], name="staff_manag_departm_577364_idx"),
                    models.Index(fields=["is_active"], name="staff_manag_is_acti_75af0f_idx"),
                ],
            },
        ),
        migrations.CreateModel(
            name="Teacher",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("date_joined", models.DateTimeField(auto_now_add=True, verbose_name="Date Joined")),
                ("date_modified", models.DateTimeField(auto_now=True, verbose_name="Date Modified")),
                ("is_deleted", models.BooleanField(default=False, verbose_name="Is Deleted")),
                ("deleted_at", models.DateTimeField(blank=True, null=True, verbose_name="Deleted At")),
                ("employee_id", models.CharField(db_index=True, max_length=32, unique=True)),
                ("department", models.CharField(blank=True, max_length=100)),
                ("specialization", models.CharField(blank=True, max_length=120)),
                ("date_of_joining", models.DateField(blank=True, null=True)),
                ("is_active", models.BooleanField(default=True)),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="teacher_profile",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["employee_id"],
                "indexes": [
                    models.Index(fields=["department"], name="staff_manag_departm_0f3fdd_idx"),
                    models.Index(fields=["is_active"], name="staff_manag_is_acti_f1ad01_idx"),
                ],
            },
        ),
    ]
