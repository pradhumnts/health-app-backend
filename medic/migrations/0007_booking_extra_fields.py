# Generated by Django 4.2.11 on 2024-06-01 10:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('medic', '0006_booking_care_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='extra_fields',
            field=models.JSONField(blank=True, null=True),
        ),
    ]
