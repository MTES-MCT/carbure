# Generated by Django 5.0.6 on 2024-12-18 10:49

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0037_alter_matierepremiere_category"),
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
                    ("AM", "AM"),
                ],
                default="CONV",
                max_length=32,
            ),
        ),
    ]