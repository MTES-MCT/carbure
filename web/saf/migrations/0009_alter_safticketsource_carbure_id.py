# Generated by Django 4.1.1 on 2022-10-28 17:01

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("saf", "0008_alter_safticket_parent_ticket_source"),
    ]

    operations = [
        migrations.AlterField(
            model_name="safticketsource",
            name="carbure_id",
            field=models.CharField(max_length=64, null=True, unique=True),
        ),
    ]
