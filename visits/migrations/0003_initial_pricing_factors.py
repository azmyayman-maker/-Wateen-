# Data migration for default PricingFactors
# T034: Create data migration for default PricingFactors

from decimal import Decimal
from django.db import migrations


def create_default_pricing_factors(apps, schema_editor):
    """Create default pricing factors for the pricing engine."""
    PricingFactor = apps.get_model("visits", "PricingFactor")

    default_factors = [
        {
            "key": "per_km_rate",
            "value": Decimal("50.00"),
            "description": "EGP per kilometer for distance-based pricing",
        },
        {
            "key": "night_multiplier",
            "value": Decimal("1.50"),
            "description": "Multiplier applied during night hours (22:00-06:00)",
        },
        {
            "key": "day_multiplier",
            "value": Decimal("1.00"),
            "description": "Multiplier applied during day hours",
        },
        {
            "key": "night_start_hour",
            "value": Decimal("22"),
            "description": "Hour when night pricing starts (24h format)",
        },
        {
            "key": "night_end_hour",
            "value": Decimal("6"),
            "description": "Hour when night pricing ends (24h format)",
        },
        {
            "key": "base_distance_km",
            "value": Decimal("5"),
            "description": "Distance in km included in base price",
        },
    ]

    for factor_data in default_factors:
        PricingFactor.objects.update_or_create(
            key=factor_data["key"],
            defaults={
                "value": factor_data["value"],
                "description": factor_data["description"],
            },
        )


def remove_default_pricing_factors(apps, schema_editor):
    """Remove default pricing factors (reverse migration)."""
    PricingFactor = apps.get_model("visits", "PricingFactor")

    default_keys = [
        "per_km_rate",
        "night_multiplier",
        "day_multiplier",
        "night_start_hour",
        "night_end_hour",
        "base_distance_km",
    ]

    PricingFactor.objects.filter(key__in=default_keys).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("visits", "0002_add_pricing_engine"),
    ]

    operations = [
        migrations.RunPython(
            create_default_pricing_factors,
            remove_default_pricing_factors,
        ),
    ]
