# Generated by Django 3.0.3 on 2020-03-24 13:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0023_auto_20200323_1604'),
    ]

    operations = [
        migrations.AddField(
            model_name='lot',
            name='ghg_total',
            field=models.FloatField(default=0.0),
        ),
    ]
