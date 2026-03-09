# Generated manually for dispatch analytics response time tracking

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("visits", "0014_visit_urgency"),
    ]

    operations = [
        migrations.AddField(
            model_name="visit",
            name="nurse_assigned_at",
            field=models.DateTimeField(
                blank=True,
                help_text="الوقت الذي تم فيه تعيين الممرض/ة للزيارة",
                null=True,
                verbose_name="وقت تعيين الممرض/ة",
            ),
        ),
    ]
