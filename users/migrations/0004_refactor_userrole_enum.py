"""
Data migration: Refactor UserRole enum.

- Maps ADMIN → SUPERADMIN
- Maps DOCTOR → NURSE
- Updates role field choices to the 4 canonical B2B2C roles
"""

from django.db import migrations, models


def migrate_legacy_roles(apps, schema_editor):
    """Remap ADMIN→SUPERADMIN and DOCTOR→NURSE."""
    CustomUser = apps.get_model("users", "CustomUser")
    CustomUser.objects.filter(role="ADMIN").update(role="SUPERADMIN")
    CustomUser.objects.filter(role="DOCTOR").update(role="NURSE")


def reverse_legacy_roles(apps, schema_editor):
    """Reverse: SUPERADMIN→ADMIN (DOCTOR→NURSE reversal is lossy - cannot recover original DOCTOR roles)."""
    CustomUser = apps.get_model("users", "CustomUser")
    CustomUser.objects.filter(role="SUPERADMIN").update(role="ADMIN")
    CustomUser.objects.filter(role="NURSE").update(role="DOCTOR")


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0003_alter_nurseprofile_verification_status_and_more"),
    ]

    operations = [
        # Step 1: Remap legacy values while both old and new are valid strings
        migrations.RunPython(
            migrate_legacy_roles,
            reverse_legacy_roles,
        ),
        # Step 2: Update the field choices to the new enum
        migrations.AlterField(
            model_name="customuser",
            name="role",
            field=models.CharField(
                choices=[
                    ("PATIENT", "Patient"),
                    ("NURSE", "Nurse"),
                    ("AGENCY_ADMIN", "Agency Admin"),
                    ("SUPERADMIN", "Super Admin"),
                ],
                default="PATIENT",
                help_text="دور المستخدم في النظام",
                max_length=15,
                verbose_name="الدور",
            ),
        ),
    ]
