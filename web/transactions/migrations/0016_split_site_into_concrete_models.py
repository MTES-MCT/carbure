"""
Migration to convert Airport, Depot, ProductionSite from proxy models to concrete
multi-table inheritance models, and move the relevant data from the `sites` table.

Strategy:
1. Delete old proxy models from Django state
2. Save data from sites columns into temporary tables (raw SQL)
3. Remove old columns from sites table
4. Create concrete child tables
5. Populate child tables from temporary tables
6. Drop temporary tables
"""

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


def save_data_to_temp_tables(apps, schema_editor):
    """Save specific fields from sites into temporary tables before columns are removed."""
    connection = schema_editor.connection
    with connection.cursor() as cursor:
        # Temp table for Depot data
        cursor.execute("""
            CREATE TEMPORARY TABLE _tmp_depot AS
            SELECT id, customs_id, accise, electrical_efficiency, thermal_efficiency, useful_temperature
            FROM sites
            WHERE site_type IN ('OTHER', 'EFS', 'EFPE', 'OIL DEPOT', 'BIOFUEL DEPOT', 'HEAT PLANT', 'POWER PLANT', 'COGENERATION PLANT', 'EFCA')
        """)  # noqa: E501

        # Temp table for ProductionSite data
        cursor.execute("""
            CREATE TEMPORARY TABLE _tmp_production_site AS
            SELECT id, date_mise_en_service, ges_option, eligible_dc, dc_number, dc_reference,
                   manager_name, manager_phone, manager_email
            FROM sites
            WHERE site_type IN ('PRODUCTION BIOLIQUID')
        """)

        # Temp table for Airport data
        cursor.execute("""
            CREATE TEMPORARY TABLE _tmp_airport AS
            SELECT id, icao_code, is_ue_airport
            FROM sites
            WHERE site_type IN ('AIRPORT')
        """)


def populate_child_tables(apps, schema_editor):
    """Populate the new child tables from temporary tables."""
    connection = schema_editor.connection
    with connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO sites_depots (site_ptr_id, customs_id, accise, electrical_efficiency, thermal_efficiency, useful_temperature)
            SELECT id, customs_id, accise, electrical_efficiency, thermal_efficiency, useful_temperature
            FROM _tmp_depot
        """)  # noqa: E501

        cursor.execute("""
            INSERT INTO sites_productionsites (site_ptr_id, date_mise_en_service, ges_option, eligible_dc, dc_number, dc_reference,
                                                     manager_name, manager_phone, manager_email)
            SELECT id, date_mise_en_service, ges_option, eligible_dc, dc_number, dc_reference,
                   manager_name, manager_phone, manager_email
            FROM _tmp_production_site
        """)  # noqa: E501

        cursor.execute("""
            INSERT INTO sites_airports (site_ptr_id, icao_code, is_ue_airport)
            SELECT id, icao_code, is_ue_airport
            FROM _tmp_airport
        """)

        # Drop temporary tables
        cursor.execute("DROP TEMPORARY TABLE IF EXISTS _tmp_depot")
        cursor.execute("DROP TEMPORARY TABLE IF EXISTS _tmp_production_site")
        cursor.execute("DROP TEMPORARY TABLE IF EXISTS _tmp_airport")


def reverse_migration(apps, schema_editor):
    """Reverse: copy data from child tables back into sites columns."""
    connection = schema_editor.connection
    with connection.cursor() as cursor:
        cursor.execute("""
            UPDATE sites s
            INNER JOIN sites_depots d ON s.id = d.site_ptr_id
            SET s.customs_id = d.customs_id,
                s.accise = d.accise,
                s.electrical_efficiency = d.electrical_efficiency,
                s.thermal_efficiency = d.thermal_efficiency,
                s.useful_temperature = d.useful_temperature
        """)

        cursor.execute("""
            UPDATE sites s
            INNER JOIN sites_productionsites p ON s.id = p.site_ptr_id
            SET s.date_mise_en_service = p.date_mise_en_service,
                s.ges_option = p.ges_option,
                s.eligible_dc = p.eligible_dc,
                s.dc_number = p.dc_number,
                s.dc_reference = p.dc_reference,
                s.manager_name = p.manager_name,
                s.manager_phone = p.manager_phone,
                s.manager_email = p.manager_email
        """)

        cursor.execute("""
            UPDATE sites s
            INNER JOIN sites_airports a ON s.id = a.site_ptr_id
            SET s.icao_code = a.icao_code,
                s.is_ue_airport = a.is_ue_airport
        """)


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0001_initial"),
        ("transactions", "0015_alter_site_collation"),
    ]

    operations = [
        # ---------------------------------------------------------------
        # Step 1: Delete old proxy models from Django state
        # ---------------------------------------------------------------
        migrations.DeleteModel(name="Airport"),
        migrations.DeleteModel(name="Depot"),
        migrations.DeleteModel(name="ProductionSite"),
        # ---------------------------------------------------------------
        # Step 2: Save data into temporary tables
        # ---------------------------------------------------------------
        migrations.RunPython(save_data_to_temp_tables, noop),
        # ---------------------------------------------------------------
        # Step 3: Remove old columns from sites table
        # ---------------------------------------------------------------
        migrations.RemoveField(model_name="site", name="customs_id"),
        migrations.RemoveField(model_name="site", name="icao_code"),
        migrations.RemoveField(model_name="site", name="accise"),
        migrations.RemoveField(model_name="site", name="electrical_efficiency"),
        migrations.RemoveField(model_name="site", name="thermal_efficiency"),
        migrations.RemoveField(model_name="site", name="useful_temperature"),
        migrations.RemoveField(model_name="site", name="ges_option"),
        migrations.RemoveField(model_name="site", name="eligible_dc"),
        migrations.RemoveField(model_name="site", name="dc_number"),
        migrations.RemoveField(model_name="site", name="dc_reference"),
        migrations.RemoveField(model_name="site", name="manager_name"),
        migrations.RemoveField(model_name="site", name="manager_phone"),
        migrations.RemoveField(model_name="site", name="manager_email"),
        migrations.RemoveField(model_name="site", name="date_mise_en_service"),
        migrations.RemoveField(model_name="site", name="is_ue_airport"),
        # ---------------------------------------------------------------
        # Step 4: Create concrete child tables
        # ---------------------------------------------------------------
        migrations.CreateModel(
            name="Airport",
            fields=[
                (
                    "site_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="transactions.site",
                    ),
                ),
                ("icao_code", models.CharField(blank=True, max_length=32)),
                ("is_ue_airport", models.BooleanField(default=True)),
            ],
            options={
                "verbose_name": "Aéroport",
                "verbose_name_plural": "Aéroports",
                "db_table": "sites_airports",
                "ordering": ["name"],
            },
            bases=("transactions.site",),
        ),
        migrations.CreateModel(
            name="Depot",
            fields=[
                (
                    "site_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="transactions.site",
                    ),
                ),
                ("customs_id", models.CharField(blank=True, max_length=32)),
                ("accise", models.CharField(blank=True, max_length=32)),
                (
                    "electrical_efficiency",
                    models.FloatField(
                        blank=True,
                        default=None,
                        help_text="Entre 0 et 1",
                        null=True,
                        validators=[
                            django.core.validators.MinValueValidator(0),
                            django.core.validators.MaxValueValidator(1),
                        ],
                    ),
                ),
                (
                    "thermal_efficiency",
                    models.FloatField(
                        blank=True,
                        default=None,
                        help_text="Entre 0 et 1",
                        null=True,
                        validators=[
                            django.core.validators.MinValueValidator(0),
                            django.core.validators.MaxValueValidator(1),
                        ],
                    ),
                ),
                (
                    "useful_temperature",
                    models.FloatField(
                        blank=True,
                        default=None,
                        help_text="En degrés Celsius",
                        null=True,
                    ),
                ),
            ],
            options={
                "verbose_name": "Dépôt",
                "verbose_name_plural": "Dépôts",
                "db_table": "sites_depots",
                "ordering": ["name"],
            },
            bases=("transactions.site",),
        ),
        migrations.CreateModel(
            name="ProductionSite",
            fields=[
                (
                    "site_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="transactions.site",
                    ),
                ),
                ("date_mise_en_service", models.DateField(blank=True, null=True)),
                (
                    "ges_option",
                    models.CharField(
                        choices=[
                            ("Default", "Valeurs par défaut"),
                            ("Actual", "Valeurs réelles"),
                            ("NUTS2", "Valeurs NUTS2"),
                        ],
                        default="Default",
                        max_length=12,
                    ),
                ),
                ("eligible_dc", models.BooleanField(default=False)),
                ("dc_number", models.CharField(blank=True, max_length=64)),
                ("dc_reference", models.CharField(blank=True, max_length=64)),
                ("manager_name", models.CharField(blank=True, max_length=64)),
                ("manager_phone", models.CharField(blank=True, max_length=64)),
                ("manager_email", models.CharField(blank=True, max_length=64)),
            ],
            options={
                "verbose_name": "Site de Production",
                "verbose_name_plural": "Sites de Production",
                "db_table": "sites_productionsites",
            },
            bases=("transactions.site",),
        ),
        # ---------------------------------------------------------------
        # Step 5: Populate child tables from temporary tables
        # ---------------------------------------------------------------
        migrations.RunPython(populate_child_tables, reverse_migration),
    ]
