# Generated manually for Pricing Engine feature (001-pricing-engine)

import django.contrib.gis.db.models.fields
import django.db.models.deletion
import uuid
from decimal import Decimal
from django.db import migrations, models


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
        migrations.AlterField(
            model_name="visit",
            name="service_type",
            field=models.ForeignKey(
                blank=True,
                help_text="نوع الخدمة التمريضية المطلوبة",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="visits",
                to="visits.servicetype",
                verbose_name="نوع الخدمة",
            ),
        ),
    ]
