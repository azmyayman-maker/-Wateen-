# Migration for EstimateLog model
# T039: Create and run migration for EstimateLog

import django.contrib.gis.db.models.fields
import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("visits", "0003_initial_pricing_factors"),
    ]

    operations = [
        migrations.CreateModel(
            name="EstimateLog",
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
                    "request_time",
                    models.DateTimeField(
                        help_text="وقت طلب التسعير",
                        verbose_name="وقت الطلب",
                    ),
                ),
                (
                    "location",
                    django.contrib.gis.db.models.fields.PointField(
                        geography=True,
                        help_text="موقع العميل عند طلب التسعير",
                        srid=4326,
                        verbose_name="موقع العميل",
                    ),
                ),
                (
                    "price_components",
                    models.JSONField(
                        help_text="تفاصيل حساب السعر للتدريب على ML",
                        verbose_name="مكونات السعر",
                    ),
                ),
                (
                    "ip_address",
                    models.GenericIPAddressField(
                        blank=True,
                        help_text="عنوان IP للعميل",
                        null=True,
                        verbose_name="عنوان IP",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="تاريخ الإنشاء"
                    ),
                ),
                (
                    "service_type",
                    models.ForeignKey(
                        blank=True,
                        help_text="نوع الخدمة المطلوبة",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="estimate_logs",
                        to="visits.servicetype",
                        verbose_name="نوع الخدمة",
                    ),
                ),
            ],
            options={
                "verbose_name": "سجل التسعير",
                "verbose_name_plural": "سجلات التسعير",
                "db_table": "visits_estimate_log",
                "ordering": ["-request_time"],
            },
        ),
        migrations.AddIndex(
            model_name="estimatelog",
            index=models.Index(
                fields=["request_time"], name="visits_est_request_time_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="estimatelog",
            index=models.Index(
                fields=["service_type"], name="visits_est_service_type_idx"
            ),
        ),
    ]
