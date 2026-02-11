from datetime import date

from elec.models.elec_charge_point import ElecChargePoint
from elec.models.elec_charge_point_application import ElecChargePointApplication
from elec.models.elec_meter import ElecMeter
from elec.models.elec_meter_reading import ElecMeterReading
from elec.models.elec_meter_reading_application import ElecMeterReadingApplication

CHARGE_POINTS_COUNT = 3
DEFAULT_YEARS = [2025]
DEFAULT_QUARTERS = [1, 2]
INITIAL_INDEX_METER = 1000
ENR_RATIO = 0.25


"""
Setup a CPO with all the data needed to use meter readings
(includes charge points, meters, meter readings applications and meter readings).
"""


def setup_cpo_with_meter_readings(
    cpo, years=DEFAULT_YEARS, quarters=DEFAULT_QUARTERS, charge_points_count=CHARGE_POINTS_COUNT
):
    # STEP 1 : Create a charge point application
    charge_point_application = ElecChargePointApplication.objects.create(
        status=ElecChargePointApplication.ACCEPTED,
        cpo=cpo,
    )

    # STEP 2 : Create charge points and associated meters
    charge_points = []
    meters = []

    for i in range(charge_points_count):
        charge_point = ElecChargePoint.objects.create(
            application=charge_point_application,
            cpo=cpo,
            charge_point_id=f"{i+1:05d}",
            current_type=ElecChargePoint.AC,
            installation_date=date(2023, 1, 1),
            is_article_2=False,
            measure_reference_point_id="MRP-001",
            station_name=f"{cpo.name} Station 00{i+1}",
            station_id=f"STAT-{cpo.id}-00{i+1}",
            nominal_power=50,
        )

        meter = ElecMeter.objects.create(
            mid_certificate=f"MID-{cpo.id}-00{i+1}",
            initial_index=INITIAL_INDEX_METER,
            initial_index_date=date(2023, 1, 1),
            charge_point=charge_point,
        )

        charge_point.current_meter = meter
        charge_point.save(update_fields=["current_meter"])

        charge_points.append(charge_point)
        meters.append(meter)

    # STEP 3 : Create meter readings applications and meter readings
    first_year = years[0]
    meter_readings = []
    meter_reading_applications = []
    for year in years:
        for quarter in quarters:
            application = ElecMeterReadingApplication.objects.create(
                cpo=cpo,
                quarter=quarter,
                year=year,
            )

            for meter in meters:
                # for each meter reading, increase the reading energy by 100 kWh compared to the previous quarter
                reading_energy = INITIAL_INDEX_METER + (year - first_year) * 1000 + quarter * 100
                meter_reading = ElecMeterReading.objects.create(
                    extracted_energy=reading_energy,
                    reading_date=date(year, quarter * 3, 1),
                    cpo=cpo,
                    application=application,
                    meter=meter,
                    enr_ratio=ENR_RATIO,
                    operating_unit=meter.charge_point.charge_point_id[:5],
                )
                meter_readings.append(meter_reading)

            meter_reading_applications.append(application)

    return charge_points, meters, meter_readings, meter_reading_applications
