# Generated by Django 3.0.3 on 2020-05-07 12:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0037_auto_20200427_1200'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='lot',
            name='attestation',
        ),
        migrations.AddField(
            model_name='lot',
            name='period',
            field=models.CharField(blank=True, default='', max_length=64),
        ),
    ]
