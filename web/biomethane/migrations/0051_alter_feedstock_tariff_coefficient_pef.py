from django.db import migrations, models


def peff_to_pef(apps, schema_editor):
    Coeff = apps.get_model("biomethane", "BiomethaneFeedstockTariffCoefficient")
    Coeff.objects.filter(coefficient="PEFF").update(coefficient="PEF")


class Migration(migrations.Migration):
    dependencies = [
        ("biomethane", "0050_biomethane_feedstock_tariff_coefficient"),
    ]

    operations = [
        migrations.RunPython(peff_to_pef, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="biomethanefeedstocktariffcoefficient",
            name="coefficient",
            field=models.CharField(
                choices=[
                    ("P1", "P1"),
                    ("P2", "P2"),
                    ("P3", "P3"),
                    ("P", "P"),
                    ("PEF", "Pef"),
                ],
                max_length=4,
                verbose_name="Coefficient",
            ),
        ),
    ]
