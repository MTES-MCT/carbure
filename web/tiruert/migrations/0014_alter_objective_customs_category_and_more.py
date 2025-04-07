# Generated by Django 5.0.6 on 2025-03-27 10:03

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("tiruert", "0013_alter_operation_status"),
    ]

    operations = [
        migrations.AlterField(
            model_name="objective",
            name="customs_category",
            field=models.CharField(
                blank=True,
                choices=[
                    ("CONV", "Conventionnel"),
                    ("ANN-IX-A", "ANNEXE IX-A"),
                    ("ANN-IX-B", "ANNEXE IX-B"),
                    ("TALLOL", "Tallol"),
                    ("OTHER", "Autre"),
                    ("EP2AM", "EP2AM"),
                ],
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name="operation",
            name="customs_category",
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
                max_length=20,
            ),
        ),
    ]
