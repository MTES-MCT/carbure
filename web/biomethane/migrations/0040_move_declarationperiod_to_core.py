# Migration to move BiomethaneDeclarationPeriod to core.DeclarationPeriod
# Uses SeparateDatabaseAndState to update Django's state without touching the database
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("biomethane", "0039_convert_biomethaneproductionunit_to_site_inheritance"),
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
