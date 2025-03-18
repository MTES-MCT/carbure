import argparse
import os
from typing import Iterable

import django
from django.db import transaction
from tqdm import tqdm

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from elec.models.elec_charge_point import ElecChargePoint
from elec.models.elec_meter_reading import ElecMeterReading  # noqa: E402
from elec.models.elec_meter_reading_application import ElecMeterReadingApplication  # noqa: E402
from elec.repositories.charge_point_repository import ChargePointRepository  # noqa: E402
from elec.repositories.meter_reading_repository import MeterReadingRepository  # noqa: E402
from transactions.models.year_config import YearConfig  # noqa: E402


@transaction.atomic
def compute_meter_reading_renewable_energy(batch):
    print("> Compute meter reading renewable energy based on previous readings")

    meter_reading_applications = ElecMeterReadingApplication.objects.all().select_related("cpo")

    renewable_shares = YearConfig.objects.all()
    renewable_share_by_year = {rs.year: rs.renewable_share for rs in renewable_shares}

    for application in tqdm(meter_reading_applications):
        meter_readings = application.elec_meter_readings.all().select_related("charge_point")
        charge_points = ChargePointRepository.get_charge_points_for_meter_readings(application.cpo)
        previous_application = MeterReadingRepository.get_previous_application(
            application.cpo, application.quarter, application.year
        )
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


def get_previous_readings_by_charge_point(
    charge_points: Iterable[ElecChargePoint],
    previous_application: ElecMeterReadingApplication,
):
    previous_readings_by_charge_point = {}

    # initialize previous readings using the first one set during the charge point registration
    for charge_point in charge_points:
        previous_readings_by_charge_point[charge_point.charge_point_id] = (
            charge_point.current_meter.initial_index if charge_point.current_meter else None
        )

    # then if there was a previous registration, use its data to specify the previous reading latest value
    if previous_application:
        for reading in previous_application.elec_meter_readings.all():
            if reading.charge_point:
                previous_readings_by_charge_point[reading.charge_point.charge_point_id] = reading.extracted_energy

    return previous_readings_by_charge_point
