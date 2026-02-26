import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0036_alter_depot_depot_type"),
        ("tiruert", "0027_operation_declaration_year"),
    ]

    operations = [
        migrations.CreateModel(
            name="ObjectiveSnapshot",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "entity",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="objective_snapshots",
                        to="core.entity",
                    ),
                ),
                ("year", models.IntegerField()),
                ("date_from", models.DateField()),
                ("date_to", models.DateField()),
                ("data", models.JSONField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Objective Snapshot",
                "verbose_name_plural": "Objective Snapshots",
                "db_table": "tiruert_objective_snapshots",
            },
        ),
        migrations.AlterUniqueTogether(
            name="objectivesnapshot",
            unique_together={("entity", "year")},
        ),
    ]
