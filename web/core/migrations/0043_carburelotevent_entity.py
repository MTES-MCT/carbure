# Generated by Django 5.0.6 on 2025-05-21 13:39

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0042_biocarburant_renewable_energy_share"),
    ]

    operations = [
        migrations.AddField(
            model_name="carburelotevent",
            name="entity",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="core.entity",
            ),
        ),
    ]
