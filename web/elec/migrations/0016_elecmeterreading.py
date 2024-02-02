# Generated by Django 4.1.7 on 2024-01-03 18:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0017_alter_carburenotification_type"),
        ("elec", "0015_elecmeterreadingapplication"),
    ]

    operations = [
        migrations.CreateModel(
            name="ElecMeterReading",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("extracted_energy", models.FloatField(blank=True, null=True)),
                (
                    "application",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="elec_meter_readings",
                        to="elec.elecmeterreadingapplication",
                    ),
                ),
                (
                    "charge_point",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="elec_meter_readings",
                        to="elec.elecchargepoint",
                    ),
                ),
                (
                    "cpo",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name="elec_meter_readings", to="core.entity"
                    ),
                ),
            ],
            options={
                "verbose_name": "Relevé électrique de point de recharge",
                "verbose_name_plural": "Relevés électriques de points de recharge",
                "db_table": "elec_meter_reading",
            },
        ),
    ]