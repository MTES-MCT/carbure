# Generated by Django 5.0.6 on 2024-09-27 13:44

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        (
            "doublecount",
            "0015_doublecountingsourcinghistory",
        ),
        ("transactions", "0005_move_data_to_site_model_backup"),
    ]

    operations = [
        migrations.AlterField(
            model_name="doublecountingapplication",
            name="production_site",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="transactions.site",
            ),
        ),
    ]