from django.db.models import Sum
from elec.models import ElecMeterReading, ElecProvisionCertificate
from transactions.models import YearConfig
import pandas as pd

def get_total_energy_amount(cpo_id, last_year):
    result = ElecProvisionCertificate.objects.filter(
        cpo_id=cpo_id, year=last_year, source=ElecProvisionCertificate.METER_READINGS
    ).aggregate(total_energy_amount=Sum("energy_amount"))
    return result["total_energy_amount"] or 0


def generate_compensate_elec_provision_certificate(last_year, percent):
    meter_readings = (
        ElecMeterReading.objects.filter(application__year=last_year)
        .values("cpo")
        .annotate(total_energy_used=Sum("energy_used_since_last_reading"))
    )
    elec_provision_certificates = []
    for meter_reading in meter_readings:
        total_energy_provision = get_total_energy_amount(
            meter_reading.get("cpo"), last_year
        )
        total_energy_used = meter_reading.get("total_energy_used") / 1000
        expected_provision = percent / 100 * total_energy_used
        delta = expected_provision - total_energy_provision
        if delta:
            elec_provision_certificates.append(
                ElecProvisionCertificate(
                    cpo_id=meter_reading.get("cpo"),
                    quarter=1,
                    year=last_year,
                    operating_unit="-",
                    energy_amount=delta,
                    remaining_energy_amount=delta,
                    compensation=True,
                )
            )
    if elec_provision_certificates:
        ElecProvisionCertificate.objects.bulk_create(elec_provision_certificates, batch_size=10)
    YearConfig.objects.filter(year=last_year).update(renewable_share=percent)
