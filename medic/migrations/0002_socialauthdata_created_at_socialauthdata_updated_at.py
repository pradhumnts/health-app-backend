# Generated by Django 4.2.11 on 2024-04-25 07:20

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('medic', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='socialauthdata',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='socialauthdata',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
