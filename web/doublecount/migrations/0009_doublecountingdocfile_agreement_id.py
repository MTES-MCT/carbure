# Generated by Django 4.1.7 on 2023-07-27 11:55

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("doublecount", "0008_alter_doublecountingapplication_table"),
    ]

    operations = [
        migrations.AddField(
            model_name="doublecountingdocfile",
            name="agreement_id",
            field=models.CharField(default="", max_length=16),
        ),
    ]
