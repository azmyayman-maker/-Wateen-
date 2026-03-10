from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('visits', '0013_recalculate_pricing'),
    ]

    operations = [
        migrations.AddField(
            model_name='visit',
            name='urgency',
            field=models.CharField(
                choices=[
                    ('LOW', 'منخفضة'),
                    ('MEDIUM', 'متوسطة'),
                    ('HIGH', 'عالية'),
                    ('CRITICAL', 'حرجة'),
                    ('SOS', 'طوارئ'),
                ],
                db_index=True,
                default='MEDIUM',
                help_text='مستوى أهمية/سرعة الزيارة',
                max_length=10,
                verbose_name='مستوى الأهمية',
            ),
        ),
    ]
