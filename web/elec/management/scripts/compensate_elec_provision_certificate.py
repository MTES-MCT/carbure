from datetime import date
from django.db.models import Sum
from elec.models import ElecMeterReading, ElecProvisionCertificate


def get_total_energy_amount(cpo_id, last_year):
    result = ElecProvisionCertificate.objects.filter(
        cpo_id=cpo_id, year=last_year
    ).aggregate(total_energy_amount=Sum("energy_amount"))
    return result["total_energy_amount"] or 0


def generate_compensate_elec_provision_certificate():
    today = date.today()
    last_year = today.year - 1

    meter_readings = (
        ElecMeterReading.objects.filter(reading_date__year=last_year)
        .values("cpo")
        .annotate(total_energy_used=Sum("energy_used_since_last_reading"))
    )
    # ElecProvisionCertificate.objects.filter(compensation=True).delete()
    for meter_reading in meter_readings:
        total_energy_provision = get_total_energy_amount(
            meter_reading.get("cpo"), last_year
        )
        total_energy_used = meter_reading.get("total_energy_used") / 1000
        expected_provision = 0.25 * total_energy_used

        diff =  expected_provision - total_energy_provision
        print(
            meter_reading.get("cpo"),
            "|",
            total_energy_provision,
            "|",
            total_energy_used,
            "|",
            expected_provision,
            diff
        )
        if diff < 0:
            pass
        else:
            elec_provision_certificate_compensation = ElecProvisionCertificate(
                cpo_id=meter_reading.get("cpo"),
                quarter=1,
                year=last_year,
                operating_unit="-",
                energy_amount=diff,
                remaining_energy_amount=0,
                compensation=True,
            )
            elec_provision_certificate_compensation.save()
