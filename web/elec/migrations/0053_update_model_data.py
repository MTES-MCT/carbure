import pandas as pd
from django.db import migrations
from django.db.models import Sum

METER_READINGS = "METER_READINGS"
MANUAL = "MANUAL"


def check_certificate_source(apps, cpo_id, last_year):
    ElecMeterReading = apps.get_model("elec", "ElecMeterReading")
    ElecProvisionCertificate = apps.get_model("elec", "ElecProvisionCertificate")
    quarters = [1, 2, 3, 4]
    for q in quarters:
        meter_readings = ElecMeterReading.objects.filter(
            application__year=last_year, application__cpo_id=cpo_id, application__quarter=q
        ).exclude(meter=None)
        data = []
        for meter_reading in meter_readings:
            data.append(
                {
                    "renewable_energy": meter_reading.renewable_energy,
                    "operating_unit": meter_reading.meter.charge_point.charge_point_id[:5],
                }
            )
        if data:
            meter_readings_df = pd.DataFrame(data)
            meter_readings_df_grouped = (
                meter_readings_df.groupby("operating_unit").agg({"renewable_energy": "sum"}).reset_index()
            )
            meter_readings_df = pd.DataFrame(data)
            meter_readings_df_grouped = (
                meter_readings_df.groupby("operating_unit").agg({"renewable_energy": "sum"}).reset_index()
            )
            for group in meter_readings_df_grouped.to_dict(orient="records"):
                operating_unit = group["operating_unit"]
                energy_amount = group["renewable_energy"] / 1000
                elec_provisions = ElecProvisionCertificate.objects.filter(
                    cpo_id=cpo_id,
                    year=last_year,
                    quarter=q,
                    compensation=False,
                    operating_unit=operating_unit,
                )
                elec_provisions.filter(energy_amount=energy_amount).update(source=METER_READINGS)
    ElecProvisionCertificate.objects.exclude(source=METER_READINGS).update(source=MANUAL)


def update_model_data(apps, schema_editor):
    last_year = 2024
    elec_meter_reading_model = apps.get_model("elec", "ElecMeterReading")
    meter_readings = (
        elec_meter_reading_model.objects.filter(application__year=last_year)
        .values("cpo")
        .annotate(total_energy_used=Sum("energy_used_since_last_reading"))
    )
    for obj in meter_readings:
        cpo_id = obj.get("cpo")
        check_certificate_source(apps, cpo_id, last_year)


class Migration(migrations.Migration):
    dependencies = [
        ("elec", "0052_elecprovisioncertificate_compensation"),
    ]

    operations = [
        migrations.RunPython(update_model_data),
    ]
