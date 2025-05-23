# Generated by Django 5.0.6 on 2025-04-07 14:36

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0040_entity_accise_number_entity_is_tiruert_liable"),
    ]

    operations = [
        migrations.AlterField(
            model_name="matierepremiere",
            name="category",
            field=models.CharField(
                choices=[
                    ("CONV", "Conventionnel"),
                    ("ANN-IX-A", "ANNEXE IX-A"),
                    ("ANN-IX-B", "ANNEXE IX-B"),
                    ("TALLOL", "Tallol"),
                    ("OTHER", "Autre"),
                    ("EP2AM", "EP2AM"),
                ],
                default="CONV",
                max_length=32,
            ),
        ),
    ]
