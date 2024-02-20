import argparse
import django
import os
from tqdm import tqdm
from django.db import transaction


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from elec.models.elec_meter_reading_application import ElecMeterReadingApplication
from elec.repositories.charge_point_repository import ChargePointRepository
from elec.repositories.meter_reading_repository import MeterReadingRepository
from elec.services.create_meter_reading_excel import get_previous_readings_by_charge_point
from transactions.models.year_config import YearConfig


from elec.models.elec_meter_reading import ElecMeterReading


@transaction.atomic
def compute_meter_reading_renewable_energy(batch):
    print(f"> Compute meter reading renewable energy based on previous readings")

    meter_reading_applications = ElecMeterReadingApplication.objects.all().select_related("cpo")

    renewable_shares = YearConfig.objects.all()
    renewable_share_by_year = {rs.year: rs.renewable_share for rs in renewable_shares}

    for application in tqdm(meter_reading_applications):
        meter_readings = application.elec_meter_readings.all().select_related("charge_point")
        charge_points = ChargePointRepository.get_charge_points_for_meter_readings(application.cpo)
        previous_application = MeterReadingRepository.get_previous_application(application.cpo, application.quarter, application.year)  # fmt:skip
        previous_readings_by_charge_point = get_previous_readings_by_charge_point(charge_points, previous_application)
        renewable_share = renewable_share_by_year.get(application.year)
        for reading in meter_readings:
            previous_extracted_energy = previous_readings_by_charge_point.get(reading.charge_point.charge_point_id) or 0
            reading.renewable_energy = (reading.extracted_energy - previous_extracted_energy) * renewable_share
        ElecMeterReading.objects.bulk_update(meter_readings, ["renewable_energy"])

    print("> Done")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Refresh charge point data and meter readings")
    parser.add_argument("--batch", dest="batch", action="store", default=1000, help="How many operations at a time")
    args = parser.parse_args()

    compute_meter_reading_renewable_energy(args.batch)
