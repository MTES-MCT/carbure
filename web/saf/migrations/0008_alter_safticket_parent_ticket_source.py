# Generated by Django 4.1.1 on 2022-10-20 16:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("saf", "0007_rename_added_by_safticket_supplier"),
    ]

    operations = [
        migrations.AlterField(
            model_name="safticket",
            name="parent_ticket_source",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="saf_tickets",
                to="saf.safticketsource",
            ),
        ),
    ]