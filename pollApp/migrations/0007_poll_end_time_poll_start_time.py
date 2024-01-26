# Generated by Django 5.0.1 on 2024-01-22 13:48

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('poll_app', '0006_alter_poll_quorum'),
    ]

    operations = [
        migrations.AddField(
            model_name='poll',
            name='end_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='poll',
            name='start_time',
            field=models.DateTimeField(blank=True, default=django.utils.timezone.now, null=True),
        ),
    ]