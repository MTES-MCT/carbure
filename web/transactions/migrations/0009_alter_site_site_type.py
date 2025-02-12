# Generated by Django 5.0.6 on 2025-01-28 10:25

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("transactions", "0008_alter_site_site_type"),
    ]

    operations = [
        migrations.AlterField(
            model_name="site",
            name="site_type",
            field=models.CharField(
                choices=[
                    ("OTHER", "Autre"),
                    ("EFS", "EFS"),
                    ("EFPE", "EFPE"),
                    ("OIL DEPOT", "OIL DEPOT"),
                    ("BIOFUEL DEPOT", "BIOFUEL DEPOT"),
                    ("HEAT PLANT", "HEAT PLANT"),
                    ("POWER PLANT", "POWER PLANT"),
                    ("COGENERATION PLANT", "COGENERATION PLANT"),
                    ("PRODUCTION BIOLIQUID", "PRODUCTION BIOLIQUID"),
                    ("EFCA", "EFCA"),
                    ("AIRPORT", "AIRPORT"),
                ],
                default="OTHER",
                max_length=32,
            ),
        ),
    ]
