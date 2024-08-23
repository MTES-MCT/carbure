# Generated by Django 4.1.1 on 2022-10-17 15:39

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0002_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="entity",
            name="entity_type",
            field=models.CharField(
                choices=[
                    ("Producteur", "Producteur"),
                    ("Opérateur", "Opérateur"),
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
