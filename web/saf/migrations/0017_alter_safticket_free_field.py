# Generated by Django 4.1.1 on 2022-11-29 09:47

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("saf", "0016_safticket_free_field"),
    ]

    operations = [
        migrations.AlterField(
            model_name="safticket",
            name="free_field",
            field=models.TextField(blank=True, default=None, max_length=64, null=True),
        ),
    ]
