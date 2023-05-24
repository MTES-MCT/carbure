# Generated by Django 4.1.7 on 2023-04-06 12:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("producers", "0001_initial"),
        ("certificates", "0002_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="doublecountingregistration",
            name="production_site",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="producers.productionsite",
            ),
        ),
    ]