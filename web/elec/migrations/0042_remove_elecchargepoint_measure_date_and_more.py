# Generated by Django 5.0.6 on 2024-08-09 13:36

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("elec", "0041_move_data_in_meter_table"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="elecchargepoint",
            name="measure_date",
        ),
        migrations.RemoveField(
            model_name="elecchargepoint",
            name="measure_energy",
        ),
        migrations.RemoveField(
            model_name="elecchargepoint",
            name="mid_id",
        ),
        migrations.RemoveField(
            model_name="elecmeterreading",
            name="charge_point",
        ),
    ]