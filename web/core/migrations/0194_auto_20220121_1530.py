# Generated by Django 3.2.8 on 2022-01-21 14:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0193_auto_20220103_1542'),
    ]

    operations = [
        migrations.AddField(
            model_name='entity',
            name='has_direct_deliveries',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='entity',
            name='has_stocks',
            field=models.BooleanField(default=False),
        ),
    ]
