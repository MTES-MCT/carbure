# Generated by Django 4.1.1 on 2022-10-20 15:18

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("saf", "0006_alter_safticket_agreement_reference"),
    ]

    operations = [
        migrations.RenameField(
            model_name="safticket",
            old_name="added_by",
            new_name="supplier",
        ),
    ]
