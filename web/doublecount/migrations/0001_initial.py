# Generated by Django 4.1.1 on 2022-09-13 10:47

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("producers", "0001_initial"),
        ("core", "0002_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="DoubleCountingAgreement",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("creation_date", models.DateTimeField(auto_now_add=True)),
                ("period_start", models.DateField()),
                ("period_end", models.DateField()),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("PENDING", "PENDING"),
                            ("INPROGRESS", "INPROGRESS"),
                            ("REJECTED", "REJECTED"),
                            ("ACCEPTED", "ACCEPTED"),
                            ("LAPSED", "LAPSED"),
                        ],
                        default="PENDING",
                        max_length=32,
                    ),
                ),
                ("dgec_validated", models.BooleanField(default=False)),
                ("dgec_validated_dt", models.DateTimeField(blank=True, null=True)),
                ("dgddi_validated", models.BooleanField(default=False)),
                ("dgddi_validated_dt", models.DateTimeField(blank=True, null=True)),
                ("dgpe_validated", models.BooleanField(default=False)),
                ("dgpe_validated_dt", models.DateTimeField(blank=True, null=True)),
                (
                    "dgddi_validator",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="dgddi_validator",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "dgec_validator",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="dgec_validator",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "dgpe_validator",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="dgpe_validator",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                ("producer", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="core.entity")),
                (
                    "producer_user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="producer_user",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "production_site",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="producers.productionsite"),
                ),
            ],
            options={
                "verbose_name": "Dossier Double Compte",
                "verbose_name_plural": "Dossiers Double Compte",
                "db_table": "double_counting_agreements",
            },
        ),
        migrations.CreateModel(
            name="DoubleCountingSourcing",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("year", models.IntegerField()),
                ("metric_tonnes", models.IntegerField()),
                (
                    "dca",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="sourcing",
                        to="doublecount.doublecountingagreement",
                    ),
                ),
                ("feedstock", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="core.matierepremiere")),
                (
                    "origin_country",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name="origin_country", to="core.pays"
                    ),
                ),
                (
                    "supply_country",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="supply_country",
                        to="core.pays",
                    ),
                ),
                (
                    "transit_country",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="transit_country",
                        to="core.pays",
                    ),
                ),
            ],
            options={
                "verbose_name": "Sourcing Double Compte",
                "verbose_name_plural": "Sourcing Double Compte",
                "db_table": "double_counting_sourcing",
            },
        ),
        migrations.CreateModel(
            name="DoubleCountingProduction",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("year", models.IntegerField()),
                ("max_production_capacity", models.IntegerField(default=0)),
                ("estimated_production", models.IntegerField(default=0)),
                ("requested_quota", models.IntegerField(default=0)),
                ("approved_quota", models.IntegerField(default=-1)),
                ("biofuel", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="core.biocarburant")),
                (
                    "dca",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="production",
                        to="doublecount.doublecountingagreement",
                    ),
                ),
                ("feedstock", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="core.matierepremiere")),
            ],
            options={
                "verbose_name": "Production Double Compte",
                "verbose_name_plural": "Production Double Compte",
                "db_table": "double_counting_production",
            },
        ),
        migrations.CreateModel(
            name="DoubleCountingDocFile",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("url", models.TextField()),
                ("file_name", models.CharField(default="", max_length=128)),
                (
                    "file_type",
                    models.CharField(
                        choices=[("SOURCING", "SOURCING"), ("DECISION", "DECISION")], default="SOURCING", max_length=128
                    ),
                ),
                ("link_expiry_dt", models.DateTimeField()),
                (
                    "dca",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="documents",
                        to="doublecount.doublecountingagreement",
                    ),
                ),
            ],
            options={
                "verbose_name": "Fichier Double Compte",
                "verbose_name_plural": "Fichiers Double Compte",
                "db_table": "double_counting_doc_files",
            },
        ),
    ]
