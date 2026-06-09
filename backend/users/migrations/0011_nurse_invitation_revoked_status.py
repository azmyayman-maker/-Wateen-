# Generated migration for NurseInvitation model enhancements

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):
    """
    Migration to add REVOKED status to InvitationStatus enum.
    
    Changes:
    - Add REVOKED status to InvitationStatus enum (backward compatible)
    
    Note: Indexes on 'token', 'status', and ('agency', 'status') are already
    declared in the model's Meta.indexes and will be created by Django
    automatically. Adding them here would cause ProgrammingError:
    "relation already exists".
    """
    
    dependencies = [
        ('users', '0010_alter_kycauditlog_action_alter_kycauditlog_agency'),
    ]

    operations = [
        # Expand InvitationStatus choices to include REVOKED.
        # For Postgres this is a no-op schema change (max_length=15 already
        # accommodates 'REVOKED'), but the AlterField keeps Django's migration
        # state in sync with the model's TextChoices.
        migrations.AlterField(
            model_name='nurseinvitation',
            name='status',
            field=models.CharField(
                choices=[
                    ('PENDING', 'قيد الانتظار'),
                    ('ACCEPTED', 'مقبول'),
                    ('EXPIRED', 'منتهي الصلاحية'),
                    ('REVOKED', 'ملغى'),
                ],
                db_index=True,
                default='PENDING',
                max_length=15,
                verbose_name='الحالة',
            ),
        ),
    ]