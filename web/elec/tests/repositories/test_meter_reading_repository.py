# Test : python web/manage.py test elec.tests.repositories.test_meter_reading_repository.TestAnnotateChargePointsWithLatestReadings --keepdb  # noqa: E501

import datetime

from django.test import TestCase

from core.models import Entity
from elec.models.elec_charge_point import ElecChargePoint
from elec.models.elec_charge_point_application import ElecChargePointApplication
from elec.models.elec_meter import ElecMeter
from elec.models.elec_meter_reading import ElecMeterReading
from elec.models.elec_meter_reading_application import ElecMeterReadingApplication
from elec.repositories.meter_reading_repository import MeterReadingRepository


class TestAnnotateChargePointsWithLatestReadings(TestCase):
    """Test for the annotate_charge_points_with_latest_readings function"""

    def setUp(self):
        """Initial setup for tests"""
        self.cpo = Entity.objects.create(
            name="CPO Test",
            entity_type=Entity.CPO,
            has_elec=True,
        )

        self.charge_point_application = ElecChargePointApplication.objects.create(
            status=ElecChargePointApplication.ACCEPTED,
            cpo=self.cpo,
        )

        self.meter = ElecMeter.objects.create(
            mid_certificate="MID_001",
            initial_index=1000.0,
            initial_index_date=datetime.date(2024, 1, 1),
            charge_point=None,
        )

        self.charge_point = ElecChargePoint.objects.create(
            application=self.charge_point_application,
            cpo=self.cpo,
            charge_point_id="FR00CP001",
            current_type="AC",
            installation_date=datetime.date(2024, 1, 1),
            current_meter=self.meter,
            station_name="Station 1",
            station_id="ST001",
            nominal_power=22.0,
        )
        self.meter.charge_point = self.charge_point
        self.meter.save()

        self.application_1 = ElecMeterReadingApplication.objects.create(
            cpo=self.cpo,
            quarter=1,
            year=2024,
            status=ElecMeterReadingApplication.ACCEPTED,
        )

        self.application_2 = ElecMeterReadingApplication.objects.create(
            cpo=self.cpo,
            quarter=2,
            year=2024,
            status=ElecMeterReadingApplication.ACCEPTED,
        )

        self.application_3 = ElecMeterReadingApplication.objects.create(
            cpo=self.cpo,
            quarter=3,
            year=2024,
            status=ElecMeterReadingApplication.ACCEPTED,
        )

    def test_with_single_meter_reading(self):
        """Test with a single ElecMeterReading and verify returned values"""

        ElecMeterReading.objects.create(
            meter=self.meter,
            cpo=self.cpo,
            application=self.application_1,
            extracted_energy=1500.0,
            renewable_energy=1200.0,
            reading_date=datetime.date(2024, 3, 31),
        )

        # Call the function
        charge_points = ElecChargePoint.objects.filter(id=self.charge_point.id)
        annotated = MeterReadingRepository.annotate_charge_points_with_latest_readings(charge_points)

        # Verify results
        cp = annotated.first()

        # Verify latest_reading_index: should be the extracted_energy value
        self.assertEqual(cp.latest_reading_index, 1500.0)

        # Verify latest_reading_date: should be the reading date
        self.assertEqual(cp.latest_reading_date, datetime.date(2024, 3, 31))

        # Verify second_latest_reading_index:
        # with a single reading, should use the meter's initial_index
        self.assertEqual(cp.second_latest_reading_index, 1000.0)

        # Verify second_latest_reading_date:
        # with a single reading, should use the meter's initial_index_date
        self.assertEqual(cp.second_latest_reading_date, datetime.date(2024, 1, 1))

    def test_without_meter(self):
        """Test with a charge point without a meter - should return 0"""

        charge_point_without_meter = ElecChargePoint.objects.create(
            application=self.charge_point_application,
            cpo=self.cpo,
            charge_point_id="FR00CP002",
            current_type="AC",
            installation_date=datetime.date(2024, 1, 1),
            current_meter=None,  # No meter
            station_name="Station 2",
            station_id="ST002",
            nominal_power=22.0,
        )

        # Call the function
        charge_points = ElecChargePoint.objects.filter(id=charge_point_without_meter.id)
        annotated = MeterReadingRepository.annotate_charge_points_with_latest_readings(charge_points)

        # Verify results
        cp = annotated.first()

        # Verify latest_reading_index: should be 0.0 when there is no meter
        self.assertEqual(cp.latest_reading_index, 0.0)

        # Verify latest_reading_date: should be date.min when there is no meter
        self.assertEqual(cp.latest_reading_date, datetime.date.min)

        # Verify second_latest_reading_index: should be 0.0
        self.assertEqual(cp.second_latest_reading_index, 0.0)

        # Verify second_latest_reading_date: should be date.min
        self.assertEqual(cp.second_latest_reading_date, datetime.date.min)

    def test_with_multiple_readings_retrieves_two_latest(self):
        """Test with multiple readings - verify that we retrieve the 2 latest readings"""
        # Create multiple readings for the same meter
        ElecMeterReading.objects.create(
            meter=self.meter,
            cpo=self.cpo,
            application=self.application_1,
            extracted_energy=1200.0,
            renewable_energy=960.0,
            reading_date=datetime.date(2024, 3, 31),
        )

        ElecMeterReading.objects.create(
            meter=self.meter,
            cpo=self.cpo,
            application=self.application_2,
            extracted_energy=1500.0,
            renewable_energy=1200.0,
            reading_date=datetime.date(2024, 6, 30),
        )

        ElecMeterReading.objects.create(
            meter=self.meter,
            cpo=self.cpo,
            application=self.application_3,
            extracted_energy=1800.0,
            renewable_energy=1440.0,
            reading_date=datetime.date(2024, 9, 30),
        )

        # Call the function
        charge_points = ElecChargePoint.objects.filter(id=self.charge_point.id)
        annotated = MeterReadingRepository.annotate_charge_points_with_latest_readings(charge_points)

        # Verify results
        cp = annotated.first()

        # latest_reading should be the last reading (application_3, highest id)
        self.assertEqual(cp.latest_reading_index, 1800.0)
        self.assertEqual(cp.latest_reading_date, datetime.date(2024, 9, 30))

        # second_latest_reading should be the second-to-last reading (application_2)
        self.assertEqual(cp.second_latest_reading_index, 1500.0)
        self.assertEqual(cp.second_latest_reading_date, datetime.date(2024, 6, 30))

    def test_with_application_id_filter(self):
        """Test with application_id parameter - verify that we filter by application"""
        # Create multiple readings for different applications
        ElecMeterReading.objects.create(
            meter=self.meter,
            cpo=self.cpo,
            application=self.application_1,
            extracted_energy=1200.0,
            renewable_energy=960.0,
            reading_date=datetime.date(2024, 3, 31),
        )

        ElecMeterReading.objects.create(
            meter=self.meter,
            cpo=self.cpo,
            application=self.application_2,
            extracted_energy=1500.0,
            renewable_energy=1200.0,
            reading_date=datetime.date(2024, 6, 30),
        )

        ElecMeterReading.objects.create(
            meter=self.meter,
            cpo=self.cpo,
            application=self.application_3,
            extracted_energy=1800.0,
            renewable_energy=1440.0,
            reading_date=datetime.date(2024, 9, 30),
        )

        charge_points = ElecChargePoint.objects.filter(id=self.charge_point.id)

        # Call the function with filtering on application_2
        annotated_filtered = MeterReadingRepository.annotate_charge_points_with_latest_readings(
            charge_points, application_id=self.application_2.id
        )
        cp_filtered = annotated_filtered.first()

        # latest_reading should be the reading from application_2
        self.assertEqual(cp_filtered.latest_reading_index, 1500.0)
        self.assertEqual(cp_filtered.latest_reading_date, datetime.date(2024, 6, 30))

        # second_latest_reading should use initial_index because we only filter on application_2
        # (there is only one reading for this application)
        self.assertEqual(cp_filtered.second_latest_reading_index, 1200.0)
        self.assertEqual(cp_filtered.second_latest_reading_date, datetime.date(2024, 3, 31))
