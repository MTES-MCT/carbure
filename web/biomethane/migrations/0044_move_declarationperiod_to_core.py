# Migration to move BiomethaneDeclarationPeriod to core.DeclarationPeriod
# Uses SeparateDatabaseAndState to update Django's state without touching the database
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("biomethane", "0043_add_type_cive_to_supply_input_and_more"),
        ("core", "0063_declarationperiod"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                # Remove BiomethaneDeclarationPeriod from biomethane app state
                migrations.DeleteModel(
                    name="BiomethaneDeclarationPeriod",
                ),
            ],
            # No database operations - table stays as-is, now managed by core.DeclarationPeriod
            database_operations=[],
        ),
    ]
