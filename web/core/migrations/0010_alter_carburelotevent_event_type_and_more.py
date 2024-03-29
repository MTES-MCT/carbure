# Generated by Django 4.1.1 on 2023-02-07 18:15

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0009_carburestock_carbure_sto_parent__9cb474_idx_and_more"),
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
                    ("DELETED_BY_ADMIN", "DELETED_BY_ADMIN"),
                ],
                max_length=32,
            ),
        ),
        migrations.AlterField(
            model_name="carburenotification",
            name="type",
            field=models.CharField(
                choices=[
                    ("CORRECTION_REQUEST", "CORRECTION_REQUEST"),
                    ("CORRECTION_DONE", "CORRECTION_DONE"),
                    ("LOTS_REJECTED", "LOTS_REJECTED"),
                    ("LOTS_RECEIVED", "LOTS_RECEIVED"),
                    ("LOTS_RECALLED", "LOTS_RECALLED"),
                    ("CERTIFICATE_EXPIRED", "CERTIFICATE_EXPIRED"),
                    ("DECLARATION_VALIDATED", "DECLARATION_VALIDATED"),
                    ("DECLARATION_CANCELLED", "DECLARATION_CANCELLED"),
                    ("DECLARATION_REMINDER", "DECLARATION_REMINDER"),
                    ("SAF_TICKET_REJECTED", "SAF_TICKET_REJECTED"),
                    ("SAF_TICKET_ACCEPTED", "SAF_TICKET_ACCEPTED"),
                    ("SAF_TICKET_RECEIVED", "SAF_TICKET_RECEIVED"),
                    ("LOTS_UPDATED_BY_ADMIN", "LOTS_UPDATED_BY_ADMIN"),
                    ("LOTS_DELETED_BY_ADMIN", "LOTS_DELETED_BY_ADMIN"),
                ],
                max_length=32,
            ),
        ),
    ]
