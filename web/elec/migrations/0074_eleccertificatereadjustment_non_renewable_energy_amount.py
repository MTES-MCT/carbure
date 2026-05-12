from django.core.validators import MinValueValidator
from django.db import migrations, models


def backfill_non_renewable_energy_amount(apps, schema_editor):
    readjustment_model = apps.get_model("elec", "ElecCertificateReadjustment")
    year_config_model = apps.get_model("transactions", "YearConfig")

    renewable_ratio_by_year = {}
    for year_config in year_config_model.objects.exclude(renewable_share__isnull=True).iterator():
        renewable_ratio = float(year_config.renewable_share) / 100
        if renewable_ratio > 0:
            renewable_ratio_by_year[year_config.year] = renewable_ratio

    for readjustment in readjustment_model.objects.filter(non_renewable_energy_amount__isnull=True).iterator():
        renewable_ratio = renewable_ratio_by_year.get(readjustment.year)
        if renewable_ratio:
            readjustment.non_renewable_energy_amount = round(float(readjustment.energy_amount) / renewable_ratio, 2)
        else:
            # Fallback when ratio is unknown for legacy data.
            readjustment.non_renewable_energy_amount = readjustment.energy_amount
        readjustment.save(update_fields=["non_renewable_energy_amount"])


class Migration(migrations.Migration):
    dependencies = [
        ("transactions", "0018_alter_site_site_type"),
        ("elec", "0073_eleccertificatereadjustment_year"),
    ]

    operations = [
        migrations.AddField(
            model_name="eleccertificatereadjustment",
            name="non_renewable_energy_amount",
            field=models.FloatField(blank=True, null=True, validators=[MinValueValidator(0.0)]),
        ),
        migrations.RunPython(backfill_non_renewable_energy_amount, migrations.RunPython.noop),
    ]
