# Generated by Django 5.0.6 on 2025-05-07 14:13

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("doublecount", "0020_convert_download_links"),
    ]

    operations = [
        migrations.AddField(
            model_name="doublecountingapplication",
            name="industrial_wastes_file_link",
            field=models.CharField(default=None, max_length=512, null=True),
        ),
    ]
