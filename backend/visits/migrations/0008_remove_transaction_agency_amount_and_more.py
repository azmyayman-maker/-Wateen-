from decimal import Decimal
import django.core.validators
import django.db.models.deletion
from django.db import migrations, models, transaction

def normalize_legacy_transaction_statuses(apps, schema_editor):
    """Map legacy status values to new 3-state choices before AlterField."""
    Transaction = apps.get_model('visits', 'Transaction')
    with transaction.atomic():
        Transaction.objects.filter(status='PENDING').update(status='ESCROWED')
        Transaction.objects.filter(status='FAILED').update(status='REFUNDED')

def reverse_normalize_transaction_statuses(apps, schema_editor):
    """Reverse mapping (best-effort) for migration rollback."""
    Transaction = apps.get_model('visits', 'Transaction')
    with transaction.atomic():
        Transaction.objects.filter(status='ESCROWED').update(status='PENDING')
        Transaction.objects.filter(status='REFUNDED').update(status='FAILED')

def backfill_legacy_data(apps, schema_editor):
    Transaction = apps.get_model('visits', 'Transaction')
    TransactionLegacyBackup = apps.get_model('visits', 'TransactionLegacyBackup')
    
    with transaction.atomic():
        for t in Transaction.objects.select_related('visit').iterator():
            # 1. Park legacy data
            TransactionLegacyBackup.objects.create(
                transaction=t,
                agency_amount=t.agency_amount,
                take_rate_percent=t.take_rate_percent,
                take_rate_amount=t.take_rate_amount,
                total_amount=t.total_amount,
                stripe_payment_intent_id=t.stripe_payment_intent_id
            )
            
            # 2. Populate new fields
            try:
                t.agency = t.visit.agency
            except Exception:
                pass
            
            t.amount_paid = t.total_amount
            t.agency_payout = t.agency_amount
            if t.take_rate_percent is not None:
                t.wateen_take_rate = t.take_rate_percent
            t.paymob_order_id = t.stripe_payment_intent_id
            
            t.save(update_fields=['agency', 'amount_paid', 'agency_payout', 'wateen_take_rate', 'paymob_order_id'])

def reverse_backfill(apps, schema_editor):
    TransactionLegacyBackup = apps.get_model('visits', 'TransactionLegacyBackup')
    with transaction.atomic():
        # Restoring data to legacy fields is not really feasible here without 
        # a lot of manual work, so we just drop the backups.
        TransactionLegacyBackup.objects.all().delete()

class Migration(migrations.Migration):

    dependencies = [
        ('users', '0008_alter_nurseprofile_syndicate_number_and_more'),
        ('visits', '0007_visit_agency_visit_distance_km_visit_distance_rate_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='TransactionLegacyBackup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('agency_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('take_rate_percent', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('take_rate_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('total_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('stripe_payment_intent_id', models.CharField(blank=True, max_length=255, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('transaction', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='legacy_backup', to='visits.transaction')),
            ],
            options={
                'db_table': 'visits_transaction_legacy_backup',
            },
        ),
        migrations.AddField(
            model_name='transaction',
            name='agency',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='transactions', to='users.agencyprofile', verbose_name='الوكالة'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='agency_payout',
            field=models.DecimalField(blank=True, decimal_places=2, editable=False, max_digits=10, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))], verbose_name='مبلغ الوكالة'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='amount_paid',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))], verbose_name='المبلغ المدفوع'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='paymob_order_id',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='معرف الطلب في Paymob'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='paymob_transaction_id',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='معرف المعاملة في Paymob'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='settled_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='تاريخ التسوية'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='wateen_take_rate',
            field=models.DecimalField(decimal_places=2, default=Decimal('15.00'), max_digits=5, validators=[django.core.validators.MinValueValidator(Decimal('0.00')), django.core.validators.MaxValueValidator(Decimal('100.00'))], verbose_name='نسبة المنصة'),
        ),
        migrations.RunPython(
            normalize_legacy_transaction_statuses,
            reverse_normalize_transaction_statuses,
        ),
        migrations.RunPython(
            backfill_legacy_data,
            reverse_backfill,
        ),
        migrations.AlterField(
            model_name='transaction',
            name='status',
            field=models.CharField(choices=[('ESCROWED', 'في الضمان'), ('SETTLED', 'تمت التسوية'), ('REFUNDED', 'تم الاسترجاع')], default='ESCROWED', max_length=20, verbose_name='الحالة'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='visit',
            field=models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='transaction', to='visits.visit', verbose_name='الزيارة'),
        ),
    ]
