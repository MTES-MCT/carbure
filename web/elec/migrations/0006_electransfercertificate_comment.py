# Generated by Django 4.1.7 on 2023-09-06 19:24

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("elec", "0005_electransfercertificate_accepted_date"),
    ]

    operations = [
        migrations.AddField(
            model_name="electransfercertificate",
            name="comment",
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
    ]