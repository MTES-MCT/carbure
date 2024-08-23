# Generated by Django 4.1.1 on 2023-01-04 18:50

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("saf", "0018_alter_safticket_free_field"),
    ]

    operations = [
        migrations.AddField(
            model_name="safticketsource",
            name="parent_ticket",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="saf.safticket",
            ),
        ),
    ]
