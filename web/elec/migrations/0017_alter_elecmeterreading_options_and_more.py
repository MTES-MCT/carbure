# Generated by Django 4.1.7 on 2024-01-11 11:50

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("elec", "0016_elecmeterreading"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="elecmeterreading",
            options={"verbose_name": "Relevé de point de recharge", "verbose_name_plural": "Relevés de points de recharge"},
        ),
        migrations.AlterModelOptions(
            name="elecmeterreadingapplication",
            options={
                "verbose_name": "Inscription de relevés de points de recharge",
                "verbose_name_plural": "Inscriptions de relevés de points de recharge",
            },
        ),
        migrations.AddField(
            model_name="elecchargepoint",
            name="latitude",
            field=models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True),
        ),
        migrations.AddField(
            model_name="elecchargepoint",
            name="longitude",
            field=models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True),
        ),
    ]
