# Generated by Django 4.1.1 on 2022-10-28 17:03

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("saf", "0009_alter_safticketsource_carbure_id"),
    ]

    operations = [
        migrations.AlterField(
            model_name="safticketsource",
            name="carbure_id",
            field=models.CharField(max_length=64, null=True),
        ),
    ]
