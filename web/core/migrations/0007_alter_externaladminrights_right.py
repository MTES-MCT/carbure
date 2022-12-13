# Generated by Django 4.1.1 on 2022-12-15 10:25

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