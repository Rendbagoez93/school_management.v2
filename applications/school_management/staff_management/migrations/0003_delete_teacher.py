# Generated migration: remove Teacher model from staff_management.
# Teacher has been moved to applications.school_management.teacher_management.

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        (
            "staff_management",
            "0002_rename_staff_manag_departm_577364_idx_staff_manag_departm_ebb757_idx_and_more",
        ),
    ]

    operations = [
        migrations.DeleteModel(
            name="Teacher",
        ),
    ]
