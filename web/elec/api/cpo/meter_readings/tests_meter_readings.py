import io
import datetime
import openpyxl
from decimal import Decimal
from core.tests_utils import setup_current_user
from core.models import Entity
from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from elec.api.cpo.meter_readings.check_application import get_application_quarter
from elec.models.elec_charge_point import ElecChargePoint

from elec.models.elec_charge_point_application import ElecChargePointApplication
from elec.models.elec_meter_reading import ElecMeterReading
from elec.models.elec_meter_reading_application import ElecMeterReadingApplication

# @TODO créer un faux csv pour mocker transport.data.gouv et contrôler les données pour les tests


class ElecCharginPointsTest(TestCase):
    def setUp(self):
        self.cpo = Entity.objects.create(
            name="CPO",
            entity_type=Entity.CPO,
            has_elec=True,
        )

        self.operator = Entity.objects.create(
            name="Operator",
            entity_type=Entity.OPERATOR,
            has_elec=True,
        )

        self.user = setup_current_user(
            self,
            "tester@carbure.local",
            "Tester",
            "gogogo",
            [(self.cpo, "RW"), (self.operator, "RW")],
        )

    def test_application_template(self):
        charge_point_application = ElecChargePointApplication.objects.create(
            status=ElecChargePointApplication.ACCEPTED,
            cpo=self.cpo,
        )

        charge_point_1 = ElecChargePoint.objects.create(
            application=charge_point_application,
            cpo=self.cpo,
            charge_point_id="FR00ABCD",
            current_type="AC",
            installation_date=datetime.date(2021, 6, 2),
            mid_id="MID_ABCD",
            measure_date=datetime.date(2022, 10, 1),
            measure_energy=1000,
            measure_reference_point_id="PRM_ABCD",
            station_name="Station",
            station_id="FR00",
            nominal_power=1000,
            cpo_name="CPO",
            cpo_siren="SIREN_ABCD",
            latitude=Decimal(12.0),
            longitude=Decimal(5.0),
        )

        charge_point_2 = ElecChargePoint.objects.create(
            application=charge_point_application,
            cpo=self.cpo,
            charge_point_id="FR00EFGH",
            current_type="AC",
            installation_date=datetime.date(2021, 6, 2),
            mid_id="MID_EFGH",
            measure_date=datetime.date(2022, 10, 1),
            measure_energy=500,
            measure_reference_point_id="PRM_EFGH",
            station_name="Station",
            station_id="FR00",
            nominal_power=500,
            cpo_name="CPO",
            cpo_siren="SIREN_EFGH",
            latitude=Decimal(12.0),
            longitude=Decimal(5.0),
        )

        charge_point_3 = ElecChargePoint.objects.create(
            application=charge_point_application,
            cpo=self.cpo,
            charge_point_id="FR00IJKL",
            current_type="AC",
            installation_date=datetime.date(2021, 6, 2),
            mid_id="MID_IJKL",
            measure_date=datetime.date(2022, 10, 1),
            measure_energy=500,
            measure_reference_point_id="PRM_IJKL",
            station_name="Station",
            station_id="FR00",
            nominal_power=500,
            cpo_name="CPO",
            cpo_siren="SIREN_IJKL",
            latitude=Decimal(12.0),
            longitude=Decimal(5.0),
            is_article_2=True,
        )

        meter_reading_application = ElecMeterReadingApplication.objects.create(
            status=ElecMeterReadingApplication.ACCEPTED,
            quarter=2,
            year=2024,
            cpo=self.cpo,
        )

        meter_reading_2 = ElecMeterReading.objects.create(
            extracted_energy=600,
            reading_date=datetime.date(2024, 5, 21),
            charge_point=charge_point_2,
            cpo=self.cpo,
            application=meter_reading_application,
        )

        response = self.client.get(
            reverse("elec-cpo-meter-readings-get-application-template"),
            {"entity_id": self.cpo.id, "quarter": 3, "year": 2024},
        )

        self.assertEqual(response.status_code, 200)

        file = io.BytesIO(response.content)
        workbook = openpyxl.load_workbook(file)
        sheet = workbook.active

        self.assertEqual(sheet["A2"].value, charge_point_1.charge_point_id)
        self.assertEqual(sheet["B2"].value, charge_point_1.measure_energy)
        self.assertEqual(sheet["C2"].value, None)
        self.assertEqual(sheet["D2"].value, None)

        self.assertEqual(sheet["A3"].value, charge_point_2.charge_point_id)
        self.assertEqual(sheet["B3"].value, meter_reading_2.extracted_energy)
        self.assertEqual(sheet["C3"].value, None)
        self.assertEqual(sheet["D3"].value, None)

        self.assertEqual(sheet["A4"].value, None)
