# Generated by Django 3.0.7 on 2020-06-15 15:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0053_lotv2_added_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='lotv2',
            name='unknown_production_site_com_date',
            field=models.CharField(blank=True, default='', max_length=64, null=True),
        ),
        migrations.AddField(
            model_name='lotv2',
            name='unknown_production_site_dbl_counting',
            field=models.CharField(blank=True, default='', max_length=64, null=True),
        ),
        migrations.AddField(
            model_name='lotv2',
            name='unknown_production_site_reference',
            field=models.CharField(blank=True, default='', max_length=64, null=True),
        ),
    ]
