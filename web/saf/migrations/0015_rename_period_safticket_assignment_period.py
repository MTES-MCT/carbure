# Generated by Django 4.1.1 on 2022-11-23 16:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("saf", "0014_rename_period_safticketsource_delivery_period"),
    ]

    operations = [
        migrations.RenameField(
            model_name="safticket",
            old_name="period",
            new_name="assignment_period",
        ),
    ]