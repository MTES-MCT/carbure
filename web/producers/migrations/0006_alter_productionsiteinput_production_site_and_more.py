# Generated by Django 5.0.6 on 2024-11-04 13:30

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("producers", "0005_alter_productionsiteinput_production_site_and_more"),
        ("transactions", "0007_depot_productionsite"),
    ]

    operations = [
        migrations.AlterField(
            model_name="productionsiteinput",
            name="production_site",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="transactions.site"),
        ),
        migrations.AlterField(
            model_name="productionsiteoutput",
            name="production_site",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="transactions.site"),
        ),
    ]
