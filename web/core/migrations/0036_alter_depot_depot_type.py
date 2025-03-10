# Generated by Django 5.0.6 on 2024-11-04 13:30

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0035_alter_carburelot_carbure_delivery_site_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="depot",
            name="depot_type",
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
                    ("EFCA", "EFCA"),
                ],
                default="OTHER",
                max_length=32,
            ),
        ),
    ]
