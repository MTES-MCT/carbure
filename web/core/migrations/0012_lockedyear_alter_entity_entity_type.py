# Generated by Django 4.1.1 on 2023-02-22 08:46

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0011_alter_carburelot_parent_lot_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="LockedYear",
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
                ("year", models.CharField(max_length=4)),
                ("locked", models.BooleanField(default=True)),
            ],
            options={
                "verbose_name": "Locked Year",
                "verbose_name_plural": "Locked Years",
                "db_table": "locked_years",
            },
        ),
        migrations.AlterField(
            model_name="entity",
            name="entity_type",
            field=models.CharField(
                choices=[
                    ("Producteur", "Producteur"),
                    ("Operateur", "Opérateur"),
                    ("Administration", "Administration"),
                    ("Trader", "Trader"),
                    ("Auditor", "Auditeur"),
                    ("Administration Externe", "Administration Externe"),
                    ("Compagnie aérienne", "Compagnie aérienne"),
                    ("Unknown", "Unknown"),
                ],
                default="Unknown",
                max_length=64,
            ),
        ),
    ]
