# Generated migration: initial Teacher model for teacher_management.

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
                "verbose_name": "Teacher",
                "verbose_name_plural": "Teachers",
                "ordering": ["employee_id"],
            },
        ),
        migrations.AddIndex(
            model_name="teacher",
            index=models.Index(fields=["department"], name="teacher_man_departm_idx"),
        ),
        migrations.AddIndex(
            model_name="teacher",
            index=models.Index(fields=["is_active"], name="teacher_man_is_acti_idx"),
        ),
    ]
