# Generated by Django 4.2.11 on 2024-06-01 10:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('medic', '0005_booking'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='care_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='care_type', to='medic.expertise'),
        ),
    ]
