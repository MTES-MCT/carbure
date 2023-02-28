# Generated by Django 4.1.1 on 2023-01-26 15:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0007_alter_externaladminrights_right"),
    ]

    operations = [
        migrations.AlterField(
            model_name="carburelotevent",
            name="event_type",
            field=models.CharField(
                choices=[
                    ("CREATED", "CREATED"),
                    ("UPDATED", "UPDATED"),
                    ("VALIDATED", "VALIDATED"),
                    ("FIX_REQUESTED", "FIX_REQUESTED"),
                    ("MARKED_AS_FIXED", "MARKED_AS_FIXED"),
                    ("FIX_ACCEPTED", "FIX_ACCEPTED"),
                    ("ACCEPTED", "ACCEPTED"),
                    ("REJECTED", "REJECTED"),
                    ("RECALLED", "RECALLED"),
                    ("DECLARED", "DECLARED"),
                    ("DELETED", "DELETED"),
                    ("DECLCANCEL", "DECLCANCEL"),
                    ("RESTORED", "RESTORED"),
                    ("CANCELLED", "CANCELLED"),
                    ("UPDATED_BY_ADMIN", "UPDATED_BY_ADMIN"),
                ],
                max_length=32,
            ),
        ),
        migrations.AddIndex(
            model_name="carburelot",
            index=models.Index(
                fields=["parent_lot"], name="carbure_lot_parent__517847_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="carburelot",
            index=models.Index(
                fields=["parent_stock"], name="carbure_lot_parent__f99f44_idx"
            ),
        ),
    ]