# Generated by Django 4.1.7 on 2023-11-28 15:37

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("doublecount", "0013_remove_doublecountingapplication_dgddi_validated_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="doublecountingapplication",
            old_name="agreement_id",
            new_name="certificate_id",
        ),
        migrations.RenameField(
            model_name="doublecountingdocfile",
            old_name="agreement_id",
            new_name="certificate_id",
        ),
    ]
