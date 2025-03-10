# Generated by Django 4.1.7 on 2023-08-07 16:10

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("doublecount", "0013_remove_doublecountingapplication_dgddi_validated_and_more"),
        ("certificates", "0004_alter_doublecountingregistration_production_site"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="doublecountingregistration",
            options={
                "ordering": ["certificate_holder"],
                "verbose_name": "Certificat Double Compte",
                "verbose_name_plural": "Certificats Double Compte",
            },
        ),
        migrations.AddField(
            model_name="doublecountingregistration",
            name="application",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="doublecount.doublecountingapplication",
            ),
        ),
    ]
