from decimal import Decimal

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('visits', '0008_remove_transaction_agency_amount_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='agency',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='transactions', to='users.agencyprofile', verbose_name='الوكالة'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='amount_paid',
            field=models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))], verbose_name='المبلغ المدفوع'),
        ),
        migrations.AlterField(
            model_name='visit',
            name='distance_km',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))], verbose_name='المسافة بالكيلومتر'),
        ),
        migrations.AlterField(
            model_name='visit',
            name='distance_rate',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))], verbose_name='سعر الكيلومتر'),
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='agency_amount',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='stripe_payment_intent_id',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='take_rate_amount',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='take_rate_percent',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='total_amount',
        ),
    ]
