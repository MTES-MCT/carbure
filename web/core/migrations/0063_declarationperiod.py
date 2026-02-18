# Migration to move BiomethaneDeclarationPeriod to core.DeclarationPeriod
# Uses SeparateDatabaseAndState - updates Django state without touching the database
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0061_matierepremiere_classification_and_more"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.CreateModel(
                    name="DeclarationPeriod",
                    fields=[
                        ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                        ("year", models.IntegerField(unique=True)),
                        ("start_date", models.DateField()),
                        ("end_date", models.DateField()),
                    ],
                    options={
                        "verbose_name": "Declaration Period",
                        "verbose_name_plural": "Declaration Periods",
                        "db_table": "biomethane_declaration_period",
                    },
                ),
            ],
            # No database operations - table already exists from biomethane app
            database_operations=[],
        ),
    ]
