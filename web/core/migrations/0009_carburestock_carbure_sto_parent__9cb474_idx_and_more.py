# Generated by Django 4.1.1 on 2023-01-30 17:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0008_alter_carburelotevent_event_type_and_more"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="carburestock",
            index=models.Index(
                fields=["parent_lot"], name="carbure_sto_parent__9cb474_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="carburestock",
            index=models.Index(
                fields=["parent_transformation"], name="carbure_sto_parent__76977a_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="carburestocktransformation",
            index=models.Index(
                fields=["source_stock"], name="carbure_sto_source__b4d70d_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="carburestocktransformation",
            index=models.Index(
                fields=["dest_stock"], name="carbure_sto_dest_st_bcd2db_idx"
            ),
        ),
    ]