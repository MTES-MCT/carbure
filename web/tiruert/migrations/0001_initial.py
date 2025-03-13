# Generated by Django 5.0.6 on 2024-11-20 10:43

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("core", "0036_alter_depot_depot_type"),
        ("transactions", "0007_depot_productionsite"),
    ]

    operations = [
        migrations.CreateModel(
            name="Operation",
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
                    "type",
                    models.CharField(
                        choices=[
                            ("INCORPORATION", "INCORPORATION"),
                            ("CESSION", "CESSION"),
                            ("TENEUR", "TENEUR"),
                            ("LIVRAISON_DIRECTE", "LIVRAISON_DIRECTE"),
                            ("MAC", "MAC"),
                        ],
                        max_length=20,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("PENDING", "PENDING"),
                            ("ACCEPTED", "ACCEPTED"),
                            ("REJECTED", "REJECTED"),
                        ],
                        default="PENDING",
                        max_length=12,
                    ),
                ),
                (
                    "customs_category",
                    models.CharField(
                        choices=[
                            ("CONV", "Conventionnel"),
                            ("ANN-IX-A", "ANNEXE IX-A"),
                            ("ANN-IX-B", "ANNEXE IX-B"),
                            ("TALLOL", "Tallol"),
                            ("OTHER", "Autre"),
                        ],
                        default="CONV",
                        max_length=32,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("validity_date", models.DateField()),
                (
                    "biofuel",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="core.biocarburant",
                    ),
                ),
                (
                    "credited_entity",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="from_operations",
                        to="core.entity",
                    ),
                ),
                (
                    "debited_entity",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="to_operations",
                        to="core.entity",
                    ),
                ),
                (
                    "depot",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="operations",
                        to="transactions.depot",
                    ),
                ),
            ],
            options={
                "verbose_name": "Opération",
                "verbose_name_plural": "Opérations",
                "db_table": "tiruert_operations",
            },
        ),
        migrations.CreateModel(
            name="OperationDetail",
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
                ("energy", models.FloatField(default=0.0)),
                ("saved_ghg", models.FloatField(default=0.0)),
                (
                    "lot",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="tiruert_operation",
                        to="core.carburelot",
                    ),
                ),
                (
                    "operation",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="details",
                        to="tiruert.operation",
                    ),
                ),
            ],
            options={
                "verbose_name": "Détail d'opération",
                "verbose_name_plural": "Détails d'opération",
                "db_table": "tiruert_operation_details",
            },
        ),
    ]
