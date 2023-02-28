# Generated by Django 4.1.1 on 2023-02-09 11:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0010_alter_carburelotevent_event_type_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="carburelot",
            name="parent_lot",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="core.carburelot",
            ),
        ),
        migrations.AlterField(
            model_name="carburelot",
            name="parent_stock",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="core.carburestock",
            ),
        ),
    ]