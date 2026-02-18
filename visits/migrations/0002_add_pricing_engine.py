# Generated manually for Pricing Engine feature (001-pricing-engine)

import django.contrib.gis.db.models.fields
import django.db.models.deletion
import uuid
from decimal import Decimal
from django.db import migrations, models


def backfill_service_types(apps, schema_editor):
    """
    Backfill ServiceType from existing Visit.service_type string values.
    Creates ServiceType records for each distinct string value found,
    then updates the temporary service_type_fk field.
    
    Uses bulk_update for performance on large tables (batches of 1000).
    """
    Visit = apps.get_model("visits", "Visit")
    ServiceType = apps.get_model("visits", "ServiceType")
    
    # Get distinct non-empty service_type string values
    distinct_types = Visit.objects.exclude(service_type="").exclude(
        service_type__isnull=True
    ).values_list("service_type", flat=True).distinct()
    
    # Create ServiceType records for each distinct value
    service_type_map = {}
    for type_name in distinct_types:
        service_type_obj, _ = ServiceType.objects.get_or_create(
            name=type_name,
            defaults={
                "base_price": Decimal("100.00"),  # Default base price
                "description": f"Migrated from legacy service_type: {type_name}",
                "is_active": True,
            }
        )
        service_type_map[type_name] = service_type_obj
    
    # OPTIMIZED: Use bulk_update with batching for performance
    # This reduces O(n) individual UPDATE queries to O(n/batch_size) queries
    visits_to_update = []
    batch_size = 1000
    
    # Use iterator() to save memory on large tables
    for visit in Visit.objects.filter(service_type__in=service_type_map.keys()).iterator():
        visit.service_type_fk = service_type_map[visit.service_type]
        visits_to_update.append(visit)
        
        # Batch process every 1000 records
        if len(visits_to_update) >= batch_size:
            Visit.objects.bulk_update(visits_to_update, ["service_type_fk"])
            visits_to_update = []
    
    # Commit remaining records
    if visits_to_update:
        Visit.objects.bulk_update(visits_to_update, ["service_type_fk"])


def reverse_backfill(apps, schema_editor):
    """
    Reverse migration: clear the service_type_fk field.
    """
    Visit = apps.get_model("visits", "Visit")
    Visit.objects.update(service_type_fk=None)


class Migration(migrations.Migration):
    dependencies = [
        ("visits", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="ServiceType",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                        verbose_name="المعرّف",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        help_text="اسم الخدمة (مثال: تمريض منزلي، علاج طبيعي)",
                        max_length=100,
                        unique=True,
                        verbose_name="اسم الخدمة",
                    ),
                ),
                (
                    "base_price",
                    models.DecimalField(
                        decimal_places=2,
                        help_text="السعر الأساسي بالجنيه المصري",
                        max_digits=10,
                        verbose_name="السعر الأساسي",
                    ),
                ),
                (
                    "description",
                    models.TextField(
                        blank=True,
                        default="",
                        help_text="وصف الخدمة",
                        verbose_name="الوصف",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="هل الخدمة متاحة للحجز",
                        verbose_name="نشط",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="تاريخ الإنشاء"
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث"),
                ),
            ],
            options={
                "verbose_name": "نوع الخدمة",
                "verbose_name_plural": "أنواع الخدمات",
                "db_table": "visits_service_type",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="PricingFactor",
            fields=[
                (
                    "key",
                    models.CharField(
                        help_text="معرف فريد للمتغير (مثال: per_km_rate)",
                        max_length=50,
                        primary_key=True,
                        serialize=False,
                        verbose_name="المفتاح",
                    ),
                ),
                (
                    "value",
                    models.DecimalField(
                        decimal_places=4,
                        help_text="قيمة المتغير",
                        max_digits=10,
                        verbose_name="القيمة",
                    ),
                ),
                (
                    "description",
                    models.CharField(
                        blank=True,
                        default="",
                        help_text="وصف للمتغير",
                        max_length=255,
                        verbose_name="الوصف",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="تاريخ الإنشاء"
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث"),
                ),
            ],
            options={
                "verbose_name": "عامل التسعير",
                "verbose_name_plural": "عوامل التسعير",
                "db_table": "visits_pricing_factor",
                "ordering": ["key"],
            },
        ),
        migrations.AddField(
            model_name="visit",
            name="base_price",
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                help_text="السعر الأساسي للخدمة",
                max_digits=10,
                null=True,
                verbose_name="السعر الأساسي",
            ),
        ),
        migrations.AddField(
            model_name="visit",
            name="distance_fee",
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                help_text="رسوم المسافة المحسوبة",
                max_digits=10,
                null=True,
                verbose_name="رسوم المسافة",
            ),
        ),
        migrations.AddField(
            model_name="visit",
            name="time_multiplier",
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                help_text="معامل الوقت (ليلي/نهاري)",
                max_digits=4,
                null=True,
                verbose_name="معامل الوقت",
            ),
        ),
        migrations.AddField(
            model_name="visit",
            name="ai_surge_coefficient",
            field=models.DecimalField(
                decimal_places=2,
                default=Decimal("1.0"),
                help_text="معامل زيادة السعر (للاستخدام المستقبلية مع ML)",
                max_digits=4,
                verbose_name="معامل الذكاء الاصطناعي",
            ),
        ),
        migrations.AddField(
            model_name="visit",
            name="final_price",
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                help_text="السعر النهائي المحسوب",
                max_digits=10,
                null=True,
                verbose_name="السعر النهائي",
            ),
        ),
        # Add temporary ForeignKey field for migration
        migrations.AddField(
            model_name="visit",
            name="service_type_fk",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="visits_temp",
                to="visits.servicetype",
                verbose_name="نوع الخدمة (مؤقت)",
            ),
        ),
        # Run backfill to populate service_type_fk from string service_type
        migrations.RunPython(
            backfill_service_types,
            reverse_code=reverse_backfill,
        ),
        # Remove the old CharField service_type
        migrations.RemoveField(
            model_name="visit",
            name="service_type",
        ),
        # Rename service_type_fk to service_type
        migrations.RenameField(
            model_name="visit",
            old_name="service_type_fk",
            new_name="service_type",
        ),
    ]
