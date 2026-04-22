# Generated manually to add role field introduced in user model.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("user", "0003_user_date_modified_user_deleted_at_user_is_deleted_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="role",
            field=models.CharField(
                blank=True,
                choices=[
                    ("Admin", "Admin"),
                    ("Principal", "Principal"),
                    ("Vice Principal", "Vice Principal"),
                    ("Teacher", "Teacher"),
                    ("Staff", "Staff"),
                    ("Librarian", "Librarian"),
                    ("Accountant", "Accountant"),
                    ("Counselor", "Counselor"),
                    ("Nurse", "Nurse"),
                    ("Receptionist", "Receptionist"),
                    ("Student", "Student"),
                    ("Parent", "Parent"),
                ],
                db_index=True,
                help_text="User's primary role in the system. Synced with Django Groups.",
                max_length=20,
                null=True,
                verbose_name="role",
            ),
        ),
    ]
