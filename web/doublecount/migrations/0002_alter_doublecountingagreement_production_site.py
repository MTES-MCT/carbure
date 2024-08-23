# Generated by Django 4.1.1 on 2022-11-24 17:45

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("producers", "0001_initial"),
        ("doublecount", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="doublecountingagreement",
            name="production_site",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="producers.productionsite",
            ),
        ),
    ]
