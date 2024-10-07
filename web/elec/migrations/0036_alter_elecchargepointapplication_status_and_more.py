# Generated by Django 5.0.6 on 2024-08-07 14:02

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("elec", "0035_elecauditsample_auditor_elecauditsample_cpo_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="elecchargepointapplication",
            name="status",
            field=models.CharField(
                choices=[
                    ("PENDING", "PENDING"),
                    ("ACCEPTED", "ACCEPTED"),
                    ("REJECTED", "REJECTED"),
                    ("AUDIT_DONE", "AUDIT_DONE"),
                    ("AUDIT_IN_PROGRESS", "AUDIT_IN_PROGRESS"),
                ],
                default="PENDING",
                max_length=32,
            ),
        ),
        migrations.AlterField(
            model_name="elecmeterreadingapplication",
            name="status",
            field=models.CharField(
                choices=[
                    ("PENDING", "PENDING"),
                    ("ACCEPTED", "ACCEPTED"),
                    ("REJECTED", "REJECTED"),
                    ("AUDIT_IN_PROGRESS", "AUDIT_IN_PROGRESS"),
                    ("AUDIT_DONE", "AUDIT_DONE"),
                ],
                default="PENDING",
                max_length=32,
            ),
        ),
    ]
