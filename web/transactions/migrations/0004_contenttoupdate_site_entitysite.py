# Generated by Django 5.0.6 on 2024-09-27 08:38

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0034_alter_entitydepot_blender"),
        ("producers", "0003_alter_productionsite_dc_number"),
        ("transactions", "0003_yearconfig_renewable_share_alter_yearconfig_locked"),
    ]

    operations = [
        migrations.CreateModel(
            name="ContentToUpdate",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("model", models.CharField(max_length=64)),
                ("field", models.CharField(max_length=64)),
                ("content_id", models.IntegerField()),
                (
                    "depot",
                    models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to="core.depot", null=True),
                ),
                (
                    "production_site",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to="producers.productionsite",
                        null=True,
                    ),
                ),
            ],
            options={
                "db_table": "_tmp_site_migration",
            },
        ),
        migrations.CreateModel(
            name="Site",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=128)),
                ("site_siret", models.CharField(blank=True, max_length=64)),
                ("customs_id", models.CharField(blank=True, max_length=32)),
                (
                    "site_type",
                    models.CharField(
                        choices=[
                            ("OTHER", "Autre"),
                            ("EFS", "EFS"),
                            ("EFPE", "EFPE"),
                            ("OIL DEPOT", "OIL DEPOT"),
                            ("BIOFUEL DEPOT", "BIOFUEL DEPOT"),
                            ("HEAT PLANT", "HEAT PLANT"),
                            ("POWER PLANT", "POWER PLANT"),
                            ("COGENERATION PLANT", "COGENERATION PLANT"),
                            ("PRODUCTION SITE", "PRODUCTION SITE"),
                            ("EFCA", "EFCA"),
                        ],
                        default="OTHER",
                        max_length=32,
                    ),
                ),
                ("address", models.CharField(blank=True, max_length=256)),
                ("postal_code", models.CharField(blank=True, max_length=32)),
                ("city", models.CharField(blank=True, max_length=128)),
                (
                    "gps_coordinates",
                    models.CharField(blank=True, default=None, max_length=64, null=True),
                ),
                (
                    "accise",
                    models.CharField(blank=True, max_length=32),
                ),
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
                (
                    "dc_number",
                    models.CharField(blank=True, max_length=64),
                ),
                (
                    "dc_reference",
                    models.CharField(blank=True, max_length=64),
                ),
                ("manager_name", models.CharField(blank=True, max_length=64)),
                ("manager_phone", models.CharField(blank=True, max_length=64)),
                ("manager_email", models.CharField(blank=True, max_length=64)),
                ("private", models.BooleanField(default=False)),
                ("is_enabled", models.BooleanField(default=True)),
                (
                    "country",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="core.pays",
                    ),
                ),
                ("date_mise_en_service", models.DateField(null=True, blank=True)),
                (
                    "created_by",
                    models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="core.entity"),
                ),
            ],
            options={
                "verbose_name": "Site de stockage de carburant",
                "verbose_name_plural": "Sites de stockage de carburant",
                "db_table": "sites",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="EntitySite",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "ownership_type",
                    models.CharField(
                        choices=[
                            ("OWN", "Propre"),
                            ("THIRD_PARTY", "Tiers"),
                            ("PROCESSING", "Processing"),
                        ],
                        default="THIRD_PARTY",
                        max_length=32,
                    ),
                ),
                (
                    "site",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="transactions.site",
                    ),
                ),
                (
                    "entity",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="core.entity"),
                ),
                ("blending_is_outsourced", models.BooleanField(default=False)),
                (
                    "blender",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="blender",
                        to="core.entity",
                    ),
                ),
            ],
            options={
                "verbose_name": "Site Entité",
                "verbose_name_plural": "Sites Entités",
                "db_table": "entity_site",
            },
        ),
    ]
