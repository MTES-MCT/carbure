# Generated by Django 5.0.6 on 2024-05-13 14:19

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("elec", "0030_merge_20240425_1159"),
    ]

    operations = [
        migrations.AlterField(
            model_name="elecchargepoint",
            name="cpo_name",
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
    ]
