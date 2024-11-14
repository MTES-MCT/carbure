# Generated by Django 5.0.6 on 2024-09-27 13:44

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("saf", "0020_safticket_saf_ticket_parent__0bbce0_idx_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="safticket",
            name="carbure_production_site",
            field=models.ForeignKey(
                blank=True,
                default=None,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="saf_production_site",
                to="transactions.site",
            ),
        ),
        migrations.AlterField(
            model_name="safticketsource",
            name="carbure_production_site",
            field=models.ForeignKey(
                blank=True,
                default=None,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="transactions.site",
            ),
        ),
    ]
