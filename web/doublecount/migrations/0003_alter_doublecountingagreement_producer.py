# Generated by Django 4.1.1 on 2022-11-24 17:57

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0006_alter_carburenotification_type"),
        ("doublecount", "0002_alter_doublecountingagreement_production_site"),
    ]

    operations = [
        migrations.AlterField(
            model_name="doublecountingagreement",
            name="producer",
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to="core.entity"),
        ),
    ]
