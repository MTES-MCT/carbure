import io
import datetime
from unittest.mock import patch
import openpyxl
from decimal import Decimal
from core.tests_utils import setup_current_user
from core.models import Entity
from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from elec.models.elec_charge_point import ElecChargePoint

from elec.models.elec_charge_point_application import ElecChargePointApplication
from elec.models.elec_meter_reading import ElecMeterReading
from elec.models.elec_meter_reading_application import ElecMeterReadingApplication
from elec.services.create_meter_reading_excel import create_meter_readings_excel
from transactions.models.year_config import YearConfig

OK_METER_READINGS = [
    {
        "charge_point_id": "FR00ABCD",
        "previous_reading": 1000,
        "current_reading": 1100,
        "reading_date": datetime.date(2024, 9, 25),
    },
    {
        "charge_point_id": "FR00EFGH",
        "previous_reading": 700,
        "current_reading": 800,
        "reading_date": datetime.date(2024, 9, 28),
    },
]

ERROR_METER_READINGS = [
    {
        "charge_point_id": "FR00ABCD",
        "previous_reading": 1000,
        "current_reading": 1100,
        "reading_date": datetime.date(2024, 9, 25),
    },
    {
        "charge_point_id": "FR00EFGH",
        "previous_reading": 700,
        "current_reading": 600,
        "reading_date": datetime.date(2024, 9, 28),
    },
    {
        "charge_point_id": "FR00IJKL",
        "previous_reading": 500,
        "current_reading": 600,
        "reading_date": datetime.date(2024, 9, 29),
    },
]


class ElecMeterReadingsTest(TestCase):
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

        YearConfig.objects.create(year=2024, renewable_share=24.92)

        self.charge_point_application = ElecChargePointApplication.objects.create(
            status=ElecChargePointApplication.ACCEPTED,
            cpo=self.cpo,
        )

        self.charge_point_1 = ElecChargePoint.objects.create(
            application=self.charge_point_application,
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

        self.charge_point_2 = ElecChargePoint.objects.create(
            application=self.charge_point_application,
            cpo=self.cpo,
            charge_point_id="FR00EFGH",
            current_type="AC",
            installation_date=datetime.date(2021, 6, 2),
            mid_id="MID_EFGH",
            measure_date=datetime.date(2022, 10, 1),
            measure_energy=700,
            measure_reference_point_id="PRM_EFGH",
            station_name="Station",
            station_id="FR00",
            nominal_power=500,
            cpo_name="CPO",
            cpo_siren="SIREN_EFGH",
            latitude=Decimal(12.0),
            longitude=Decimal(5.0),
        )

        self.charge_point_3 = ElecChargePoint.objects.create(
            application=self.charge_point_application,
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

        self.meter_reading_application = ElecMeterReadingApplication.objects.create(
            status=ElecMeterReadingApplication.ACCEPTED,
            quarter=2,
            year=2024,
            cpo=self.cpo,
        )

        self.meter_reading_2 = ElecMeterReading.objects.create(
            extracted_energy=800,
            renewable_energy=24.92,
            reading_date=datetime.date(2024, 5, 21),
            charge_point=self.charge_point_2,
            cpo=self.cpo,
            application=self.meter_reading_application,
        )

    def test_application_template(self):
        response = self.client.get(
            reverse("elec-cpo-meter-readings-get-application-template"),
            {"entity_id": self.cpo.id, "quarter": 3, "year": 2024},
        )

        self.assertEqual(response.status_code, 200)

        file = io.BytesIO(response.content)
        workbook = openpyxl.load_workbook(file)
        sheet = workbook.active

        self.assertEqual(sheet["A2"].value, self.charge_point_1.charge_point_id)
        self.assertEqual(sheet["B2"].value, self.charge_point_1.measure_energy)
        self.assertEqual(sheet["C2"].value, None)
        self.assertEqual(sheet["D2"].value, None)

        self.assertEqual(sheet["A3"].value, self.charge_point_2.charge_point_id)
        self.assertEqual(sheet["B3"].value, self.meter_reading_2.extracted_energy)
        self.assertEqual(sheet["C3"].value, None)
        self.assertEqual(sheet["D3"].value, None)

        self.assertEqual(sheet["A4"].value, None)

    def test_check_application_error(self):
        excel_file = create_meter_readings_excel(
            name="readings",
            quarter=3,
            year=2024,
            meter_readings_data=ERROR_METER_READINGS,
        )

        response = self.client.post(
            reverse("elec-cpo-meter-readings-check-application"),
            {
                "entity_id": self.cpo.id,
                "quarter": 3,
                "year": 2024,
                "file": SimpleUploadedFile("readings.xlsx", excel_file.read()),
            },
        )

        data = response.json()
        self.assertEqual(response.status_code, 400)

        self.assertEqual(
            data,
            {
                "status": "error",
                "error": "VALIDATION_FAILED",
                "data": {
                    "file_name": "readings.xlsx",
                    "quarter": 3,
                    "year": 2024,
                    "pending_application_already_exists": False,
                    "meter_reading_count": 2,
                    "error_count": 1,
                    "errors": [
                        {
                            "error": "INVALID_DATA",
                            "line": 3,
                            "meta": {
                                "extracted_energy": ["La quantité d'énergie soutirée est inférieure au précédent relevé."]
                            },
                        },
                    ],
                },
            },
        )

    def test_check_application_ok(self):
        excel_file = create_meter_readings_excel(
            name="readings",
            quarter=3,
            year=2024,
            meter_readings_data=OK_METER_READINGS,
        )

        response = self.client.post(
            reverse("elec-cpo-meter-readings-check-application"),
            {
                "entity_id": self.cpo.id,
                "quarter": 3,
                "year": 2024,
                "file": SimpleUploadedFile("readings.xlsx", excel_file.read()),
            },
        )

        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            data,
            {
                "status": "success",
                "data": {
                    "file_name": "readings.xlsx",
                    "meter_reading_count": 2,
                    "quarter": 3,
                    "year": 2024,
                    "errors": [],
                    "error_count": 0,
                    "pending_application_already_exists": False,
                },
            },
        )

    def test_add_application_error(self):
        excel_file = create_meter_readings_excel(
            name="readings",
            quarter=3,
            year=2024,
            meter_readings_data=ERROR_METER_READINGS,
        )

        response = self.client.post(
            reverse("elec-cpo-meter-readings-add-application"),
            {
                "entity_id": self.cpo.id,
                "quarter": 3,
                "year": 2024,
                "file": SimpleUploadedFile("readings.xlsx", excel_file.read()),
            },
        )

        data = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            data,
            {
                "status": "error",
                "error": "VALIDATION_FAILED",
            },
        )

    def test_add_application_ok(self):
        excel_file = create_meter_readings_excel(
            name="readings",
            quarter=3,
            year=2024,
            meter_readings_data=OK_METER_READINGS,
        )

        response = self.client.post(
            reverse("elec-cpo-meter-readings-add-application"),
            {
                "entity_id": self.cpo.id,
                "quarter": 3,
                "year": 2024,
                "file": SimpleUploadedFile("readings.xlsx", excel_file.read()),
            },
        )

        data = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data, {"status": "success"})

        last_application = ElecMeterReadingApplication.objects.last()

        self.assertEqual(last_application.quarter, 3)
        self.assertEqual(last_application.year, 2024)
        self.assertEqual(last_application.elec_meter_readings.count(), 2)

        readings = last_application.elec_meter_readings.all()
        reading_1 = readings[0]
        reading_2 = readings[1]

        self.assertEqual(reading_1.extracted_energy, 1100)
        self.assertEqual(reading_1.reading_date, datetime.date(2024, 9, 25))
        self.assertEqual(reading_2.extracted_energy, 800)
        self.assertEqual(reading_2.reading_date, datetime.date(2024, 9, 28))

    def test_get_applications(self):
        mocked_get_application_quarter = patch("elec.api.cpo.meter_readings.applications.get_application_quarter").start()  # fmt:skip
        mocked_get_application_quarter.return_value = (2024, 3)

        mocked_get_application_deadline = patch("elec.api.cpo.meter_readings.applications.get_application_deadline").start()  # fmt:skip
        mocked_get_application_deadline.return_value = (datetime.date(2024, 10, 15), "HIGH")

        response = self.client.get(
            reverse("elec-cpo-meter-readings-get-applications"),
            {"entity_id": self.cpo.id},
        )

        application = ElecMeterReadingApplication.objects.last()
        application_date = application.created_at.isoformat()

        self.maxDiff = None
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            data,
            {
                "data": {
                    "applications": [
                        {
                            "application_date": application_date,
                            "charge_point_count": 1,
                            "cpo": {"entity_type": "Charge Point Operator", "id": self.cpo.id, "name": "CPO"},
                            "energy_total": 24.92,
                            "id": application.id,
                            "quarter": 2,
                            "status": "ACCEPTED",
                            "year": 2024,
                        }
                    ],
                    "current_application": None,
                    "current_application_period": {
                        "deadline": "2024-10-15",
                        "quarter": 3,
                        "urgency_status": "HIGH",
                        "year": 2024,
                    },
                },
                "status": "success",
            },
        )

    def test_get_application_details(self):
        response = self.client.get(
            reverse("elec-cpo-meter-readings-get-application-details"),
            {"entity_id": self.cpo.id, "application_id": self.meter_reading_application.id},
        )

        data = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            data,
            {
                "status": "success",
                "data": [
                    {
                        "charge_point_id": "FR00EFGH",
                        "previous_reading": 700.0,
                        "current_reading": 800.0,
                        "reading_date": "2024-05-21",
                    },
                ],
            },
        )
