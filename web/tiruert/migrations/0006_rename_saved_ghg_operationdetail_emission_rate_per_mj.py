# Generated by Django 5.0.6 on 2025-01-07 11:44

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("tiruert", "0005_remove_operation_depot_operation_from_depot_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="operationdetail",
            old_name="saved_ghg",
            new_name="emission_rate_per_mj",
        ),
    ]
