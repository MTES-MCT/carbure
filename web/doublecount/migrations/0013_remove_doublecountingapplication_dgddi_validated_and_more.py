# Generated by Django 4.1.7 on 2023-08-07 07:42

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("doublecount", "0012_alter_doublecountingapplication_status"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="doublecountingapplication",
            name="dgddi_validated",
        ),
        migrations.RemoveField(
            model_name="doublecountingapplication",
            name="dgddi_validated_dt",
        ),
        migrations.RemoveField(
            model_name="doublecountingapplication",
            name="dgddi_validator",
        ),
        migrations.RemoveField(
            model_name="doublecountingapplication",
            name="dgec_validated",
        ),
        migrations.RemoveField(
            model_name="doublecountingapplication",
            name="dgec_validated_dt",
        ),
        migrations.RemoveField(
            model_name="doublecountingapplication",
            name="dgec_validator",
        ),
        migrations.RemoveField(
            model_name="doublecountingapplication",
            name="dgpe_validated",
        ),
        migrations.RemoveField(
            model_name="doublecountingapplication",
            name="dgpe_validated_dt",
        ),
        migrations.RemoveField(
            model_name="doublecountingapplication",
            name="dgpe_validator",
        ),
    ]
