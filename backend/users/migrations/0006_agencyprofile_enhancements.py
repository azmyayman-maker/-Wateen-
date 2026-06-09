import django.contrib.gis.db.models.fields
import django.db.models.deletion
from django.contrib.postgres.indexes import GistIndex
from django.db import migrations, models


def deduplicate_agency_users(apps, schema_editor):
    CustomUser = apps.get_model('users', 'CustomUser')
    AgencyProfile = apps.get_model('users', 'AgencyProfile')
    
    for agency in AgencyProfile.objects.all():
        users = CustomUser.objects.filter(agency=agency).order_by('date_joined')
        if users.count() > 1:
            first_user = users.first()
            CustomUser.objects.filter(agency=agency).exclude(pk=first_user.pk).update(agency=None)

class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_add_agency_fk_to_customuser'),
    ]

    operations = [
        # Data deduplication step before uniqueness constraint applies
        migrations.RunPython(deduplicate_agency_users, reverse_code=migrations.RunPython.noop),

        # Change `rating` to FloatField from DecimalField
        migrations.AlterField(
            model_name='agencyprofile',
            name='rating',
            field=models.FloatField(default=0.0, verbose_name='التقييم'),
        ),
        
        # Change `dispatch_mode` default from AUTO to MANUAL
        migrations.AlterField(
            model_name='agencyprofile',
            name='dispatch_mode',
            field=models.CharField(
                choices=[('AUTO', 'آلي'), ('MANUAL', 'يدوي')],
                default='MANUAL',
                max_length=10,
                verbose_name='آلية التوزيع'
            ),
        ),
        
        # Change `agency` relation on CustomUser from ForeignKey to OneToOneField
        migrations.AlterField(
            model_name='customuser',
            name='agency',
            field=models.OneToOneField(
                blank=True,
                help_text='الشركة التابع لها المستخدم (للمديرين)',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='admin_user',
                to='users.agencyprofile',
                verbose_name='الشركة/الوكالة'
            ),
        ),
        
        # Add GistIndex to coverage_polygon
        migrations.AddIndex(
            model_name='agencyprofile',
            index=GistIndex(fields=['coverage_polygon'], name='users_agenc_coverag_bb79fd_gist'),
        ),
    ]
