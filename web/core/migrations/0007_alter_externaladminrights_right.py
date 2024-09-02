# Generated by Django 4.1.1 on 2023-01-04 18:50

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0006_alter_carburenotification_type"),
    ]

    operations = [
        migrations.AlterField(
            model_name="externaladminrights",
            name="right",
            field=models.CharField(
                choices=[
                    ("DCA", "DCA"),
                    ("AGRIMER", "AGRIMER"),
                    ("TIRIB", "TIRIB"),
                    ("AIRLINE", "AIRLINE"),
                ],
                default="",
                max_length=32,
            ),
        ),
    ]
