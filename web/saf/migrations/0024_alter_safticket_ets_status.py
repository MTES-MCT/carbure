# Generated by Django 5.0.6 on 2025-02-03 13:54

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("saf", "0023_safticket_ets_declaration_date_safticket_ets_status_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="safticket",
            name="ets_status",
            field=models.CharField(
                blank=True,
                choices=[
                    ("ETS_VALUATION", "Valorisation ETS"),
                    ("OUTSIDE_ETS", "Hors ETS (volontaire)"),
                    ("NOT_CONCERNED", "Non concerné"),
                ],
                max_length=16,
                null=True,
            ),
        ),
    ]
