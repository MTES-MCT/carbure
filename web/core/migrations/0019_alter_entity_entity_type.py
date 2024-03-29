# Generated by Django 4.1.7 on 2024-02-02 11:29

from django.db import migrations, models


def rename_power_plant(apps, schema_editor):
    Entity = apps.get_model("core", "Entity")
    entities_to_update = Entity.objects.filter(entity_type="Power Station")
    entities_to_update.update(entity_type="Power or Heat Producer")


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0018_alter_carburelot_delivery_type_and_more"),
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
                    ("Power or Heat Producer", "Producteur d'électricité ou de chaleur"),
                ],
                default="Unknown",
                max_length=64,
            ),
        ),
        migrations.RunPython(rename_power_plant, migrations.RunPython.noop),
    ]
