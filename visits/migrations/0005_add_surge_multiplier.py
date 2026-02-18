# Add surge_multiplier field to ServiceType
# Ticket 2.4 Remediation: Pricing Engine Scaffolding

from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("visits", "0004_add_estimate_log"),
    ]

    operations = [
        migrations.AddField(
            model_name="servicetype",
            name="surge_multiplier",
            field=models.DecimalField(
                default=Decimal("1.0"),
                decimal_places=2,
                max_digits=4,
                help_text="معامل زيادة السعر (الافتراضي 1.0)",
                verbose_name="معامل الزيادة",
            ),
        ),
    ]
