# Generated manually for multi-table inheritance conversion

import django.db.models.deletion
from django.db import migrations, models


def migrate_data_forward(apps, schema_editor):
    """
    Migrate BiomethaneProductionUnit data to Site parent model.
    """
    BiomethaneProductionUnit = apps.get_model("biomethane", "BiomethaneProductionUnit")
    Site = apps.get_model("transactions", "Site")
    Pays = apps.get_model("core", "Pays")

    # Get France as default country
    france = Pays.objects.filter(code_pays="FR").first()

    for unit in BiomethaneProductionUnit.objects.all():
        # Create Site entry for this BiomethaneProductionUnit
        site = Site.objects.create(
            name=unit.unit_name or f"Unité de production {unit.id}",
            site_siret=unit.siret_number or "",
            site_type="PRODUCTION BIOGAZ",
            address=unit.company_address or "",
            postal_code=unit.postal_code or "",
            city=unit.city or "",
            country=france,
            private=False,
            is_enabled=True,
            created_by=unit.producer,
        )

        # Update the unit to point to the new Site
        unit.site_ptr_id = site.pk
        unit.save()


def migrate_data_backward(apps, schema_editor):
    """
    Reverse the migration - copy data back from Site to BiomethaneProductionUnit fields.
    """
    BiomethaneProductionUnit = apps.get_model("biomethane", "BiomethaneProductionUnit")

    for unit in BiomethaneProductionUnit.objects.select_related("site_ptr").all():
        if unit.site_ptr:
            unit.unit_name = unit.site_ptr.name
            unit.siret_number = unit.site_ptr.site_siret
            unit.company_address = unit.site_ptr.address
            unit.postal_code = unit.site_ptr.postal_code
            unit.city = unit.site_ptr.city
            unit.save()


class Migration(migrations.Migration):
    dependencies = [
        ("biomethane", "0038_merge_20260211_1431"),
        ("transactions", "0018_alter_site_site_type"),
        ("core", "0061_matierepremiere_classification_and_more"),
    ]

    operations = [
        # Step 1: Add site_ptr as nullable field first
        migrations.AddField(
            model_name="biomethaneproductionunit",
            name="site_ptr",
            field=models.OneToOneField(
                auto_created=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                parent_link=True,
                to="transactions.site",
            ),
        ),
        # Step 2: Run data migration
        migrations.RunPython(migrate_data_forward, migrate_data_backward),
        # Step 3 & 4: Change primary key atomically (DB + Django state)
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    # Forward: drop old PK, add new PK in one statement
                    sql="""
                        ALTER TABLE biomethane_production_unit
                        DROP PRIMARY KEY,
                        DROP COLUMN id,
                        MODIFY COLUMN site_ptr_id INT NOT NULL,
                        ADD PRIMARY KEY (site_ptr_id)
                    """,
                    # Reverse: recreate old id column and make it PK
                    reverse_sql="""
                        ALTER TABLE biomethane_production_unit
                        DROP PRIMARY KEY,
                        ADD COLUMN id INT AUTO_INCREMENT PRIMARY KEY FIRST,
                        MODIFY COLUMN site_ptr_id INT NULL
                    """,
                ),
            ],
            state_operations=[
                # Remove old id field from Django state
                migrations.RemoveField(
                    model_name="biomethaneproductionunit",
                    name="id",
                ),
                # Update site_ptr to be primary key in Django state
                migrations.AlterField(
                    model_name="biomethaneproductionunit",
                    name="site_ptr",
                    field=models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="transactions.site",
                    ),
                ),
            ],
        ),
        # Step 5: Remove old fields that are now in Site
        migrations.RemoveField(
            model_name="biomethaneproductionunit",
            name="unit_name",
        ),
        migrations.RemoveField(
            model_name="biomethaneproductionunit",
            name="siret_number",
        ),
        migrations.RemoveField(
            model_name="biomethaneproductionunit",
            name="company_address",
        ),
        migrations.RemoveField(
            model_name="biomethaneproductionunit",
            name="postal_code",
        ),
        migrations.RemoveField(
            model_name="biomethaneproductionunit",
            name="city",
        ),
        # Step 6: Rename the table
        migrations.AlterModelTable(
            name="biomethaneproductionunit",
            table="sites_biomethaneproductionunits",
        ),
    ]
