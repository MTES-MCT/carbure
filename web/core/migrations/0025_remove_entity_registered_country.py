# Generated by Django 4.1.7 on 2024-03-26 14:39

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0024_entity_country_rename"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="entity",
            name="registered_country",
        ),
    ]
