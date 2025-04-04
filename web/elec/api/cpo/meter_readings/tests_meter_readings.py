# Test : python web/manage.py test elec.api.cpo.meter_readings.tests_meter_readings.ElecMeterReadingsTest --keepdb


import datetime
import io
from decimal import Decimal
from unittest import mock
from unittest.mock import patch

import openpyxl
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from core.models import Entity
from core.tests_utils import setup_current_user
from elec.models.elec_charge_point import ElecChargePoint
from elec.models.elec_charge_point_application import ElecChargePointApplication
from elec.models.elec_meter import ElecMeter
from elec.models.elec_meter_reading import ElecMeterReading
from elec.models.elec_meter_reading_application import ElecMeterReadingApplication
from elec.services.create_meter_reading_excel import create_meter_readings_excel
from transactions.models.year_config import YearConfig

OK_METER_READINGS = [
    {
        "charge_point_id": "FR00ABCD",
        "previous_reading": 1000,
        "current_reading": 1100,
        "reading_date": datetime.date(2025, 9, 25),
    },
    {
        "charge_point_id": "FR00EFGH",
        "previous_reading": 700,
        "current_reading": 800,
        "reading_date": datetime.date(2025, 9, 28),
    },
]

ERROR_METER_READINGS = [
    {
        # no problemo
        "charge_point_id": "FR00ABCD",
        "previous_reading": 1000,
        "current_reading": 1100,
        "reading_date": datetime.date(2025, 9, 25),
    },
    {
        # new energy is smaller than previous one
        "charge_point_id": "FR00EFGH",
        "previous_reading": 700,
        "current_reading": 600,
        "reading_date": datetime.date(2025, 9, 28),
    },
    {
        # PDC is listed twice
        "charge_point_id": "FR00IJKL",
        "previous_reading": 500,
        "current_reading": 600,
        "reading_date": datetime.date(2025, 9, 29),
    },
    {
        # PDC is listed twice
        "charge_point_id": "FR00IJKL",
        "previous_reading": 500,
        "current_reading": 800,
        "reading_date": datetime.date(2025, 9, 29),
    },
    {
        # PDC is not yet registered
        "charge_point_id": "FR00IJKAA",
        "previous_reading": 300,
        "current_reading": 900,
        "reading_date": datetime.date(2025, 9, 29),
    },
    {
        # reading date is outside of current quarter
        "charge_point_id": "FR00MNOP",
        "previous_reading": 1000,
        "current_reading": 2000,
        "reading_date": datetime.date(2025, 6, 29),
    },
    {
        # PDC has no registered meter
        "charge_point_id": "FR00QRST",
        "previous_reading": 1000,
        "current_reading": 2000,
        "reading_date": datetime.date(2025, 9, 28),
    },
    {
        # reading date is before previous one (+ before beginning of quarter)
        "charge_point_id": "FR00UVWX",
        "previous_reading": 500,
        "current_reading": 2000,
        "reading_date": datetime.date(2024, 3, 25),  # previous: date(2024, 3, 28)
    },
    {
        # facteur_de_charge is greater than 100%
        "charge_point_id": "FR11ABCD",
        "previous_reading": 500,
        "current_reading": 2000000,
        "reading_date": datetime.date(2025, 9, 28),
    },
    {
        # reading date is before beginning of quarter
        "charge_point_id": "FR11EFGH",
        "previous_reading": 500,
        "current_reading": 600,
        "reading_date": datetime.date(2025, 6, 28),
    },
    {
        # reading date is after end of quarter
        "charge_point_id": "FR11IJKL",
        "previous_reading": 500,
        "current_reading": 600,
        "reading_date": datetime.date(2025, 10, 25),
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
        YearConfig.objects.create(year=2025, renewable_share=25)

        self.charge_point_application = ElecChargePointApplication.objects.create(
            status=ElecChargePointApplication.ACCEPTED,
            cpo=self.cpo,
        )

        self.meter1 = ElecMeter.objects.create(
            mid_certificate="MID_ABCD",
            initial_index=1000,
            initial_index_date=datetime.date(2024, 3, 30),
            charge_point=None,
        )

        self.meter2 = ElecMeter.objects.create(
            mid_certificate="MID_EFGH",
            initial_index=700,
            initial_index_date=datetime.date(2024, 3, 29),
            charge_point=None,
        )

        self.meter3 = ElecMeter.objects.create(
            mid_certificate="MID_IJKL",
            initial_index=500,
            initial_index_date=datetime.date(2024, 3, 28),
            charge_point=None,
        )

        self.meter4 = ElecMeter.objects.create(
            mid_certificate="MID_MNOP",
            initial_index=500,
            initial_index_date=datetime.date(2024, 3, 28),
            charge_point=None,
        )

        self.charge_point_1 = ElecChargePoint.objects.create(
            application=self.charge_point_application,
            cpo=self.cpo,
            charge_point_id="FR00ABCD",
            current_type="AC",
            installation_date=datetime.date(2021, 6, 2),
            current_meter=self.meter1,
            measure_reference_point_id="PRM_ABCD",
            station_name="Station",
            station_id="FR00",
            nominal_power=10,
            cpo_name="CPO",
            cpo_siren="SIREN_ABCD",
            latitude=Decimal(12.0),
            longitude=Decimal(5.0),
        )

        self.meter1.charge_point = self.charge_point_1
        self.meter1.save()

        self.charge_point_2 = ElecChargePoint.objects.create(
            application=self.charge_point_application,
            cpo=self.cpo,
            charge_point_id="FR00EFGH",
            current_type="AC",
            installation_date=datetime.date(2021, 6, 2),
            current_meter=self.meter2,
            measure_reference_point_id="PRM_EFGH",
            station_name="Station",
            station_id="FR00",
            nominal_power=50,
            cpo_name="CPO",
            cpo_siren="SIREN_EFGH",
            latitude=Decimal(12.0),
            longitude=Decimal(5.0),
        )

        self.meter2.charge_point = self.charge_point_2
        self.meter2.save()

        self.charge_point_3 = ElecChargePoint.objects.create(
            application=self.charge_point_application,
            cpo=self.cpo,
            charge_point_id="FR00IJKL",
            current_type="AC",
            installation_date=datetime.date(2021, 6, 2),
            current_meter=self.meter3,
            measure_reference_point_id="PRM_IJKL",
            station_name="Station",
            station_id="FR00",
            nominal_power=50,
            cpo_name="CPO",
            cpo_siren="SIREN_IJKL",
            latitude=Decimal(12.0),
            longitude=Decimal(5.0),
            is_article_2=True,
        )

        self.meter3.charge_point = self.charge_point_3
        self.meter3.save()

        self.charge_point_4 = ElecChargePoint.objects.create(
            application=self.charge_point_application,
            cpo=self.cpo,
            charge_point_id="FR00MNOP",
            current_type="AC",
            installation_date=datetime.date(2021, 6, 2),
            current_meter=self.meter4,
            measure_reference_point_id="PRM_MNOP",
            station_name="Station",
            station_id="FR00",
            nominal_power=50,
            cpo_name="CPO",
            cpo_siren="SIREN_MNOP",
            latitude=Decimal(12.0),
            longitude=Decimal(5.0),
        )

        self.meter4.charge_point = self.charge_point_4
        self.meter4.save()

        self.charge_point_5 = ElecChargePoint.objects.create(
            application=self.charge_point_application,
            cpo=self.cpo,
            charge_point_id="FR00QRST",
            current_type="AC",
            installation_date=datetime.date(2021, 6, 2),
            current_meter=None,
            measure_reference_point_id="PRM_QRST",
            station_name="Station",
            station_id="FR00",
            nominal_power=50,
            cpo_name="CPO",
            cpo_siren="SIREN_MNOP",
            latitude=Decimal(12.0),
            longitude=Decimal(5.0),
        )

        self.charge_point_6 = ElecChargePoint.objects.create(
            application=self.charge_point_application,
            cpo=self.cpo,
            charge_point_id="FR00UVWX",
            current_type="AC",
            installation_date=datetime.date(2021, 6, 2),
            current_meter=self.meter4,
            measure_reference_point_id="PRM_UVWX",
            station_name="Station",
            station_id="FR00",
            nominal_power=50,
            cpo_name="CPO",
            cpo_siren="SIREN_UVWX",
            latitude=Decimal(12.0),
            longitude=Decimal(5.0),
        )

        self.charge_point_7 = ElecChargePoint.objects.create(
            application=self.charge_point_application,
            cpo=self.cpo,
            charge_point_id="FR11ABCD",
            current_type="AC",
            installation_date=datetime.date(2021, 6, 2),
            current_meter=self.meter4,
            measure_reference_point_id="PRM_ABCD1",
            station_name="Station",
            station_id="FR00",
            nominal_power=50,
            cpo_name="CPO",
            cpo_siren="SIREN_ABCD1",
            latitude=Decimal(12.0),
            longitude=Decimal(5.0),
        )

        self.charge_point_8 = ElecChargePoint.objects.create(
            application=self.charge_point_application,
            cpo=self.cpo,
            charge_point_id="FR11EFGH",
            current_type="AC",
            installation_date=datetime.date(2021, 6, 2),
            current_meter=self.meter4,
            measure_reference_point_id="PRM_EFGH",
            station_name="Station",
            station_id="FR00",
            nominal_power=50,
            cpo_name="CPO",
            cpo_siren="SIREN_EFGH",
            latitude=Decimal(12.0),
            longitude=Decimal(5.0),
        )

        self.charge_point_9 = ElecChargePoint.objects.create(
            application=self.charge_point_application,
            cpo=self.cpo,
            charge_point_id="FR11IJKL",
            current_type="AC",
            installation_date=datetime.date(2021, 6, 2),
            current_meter=self.meter4,
            measure_reference_point_id="PRM_IJKL",
            station_name="Station",
            station_id="FR00",
            nominal_power=50,
            cpo_name="CPO",
            cpo_siren="SIREN_IJKL",
            latitude=Decimal(12.0),
            longitude=Decimal(5.0),
        )

        self.meter_reading_application = ElecMeterReadingApplication.objects.create(
            status=ElecMeterReadingApplication.ACCEPTED,
            quarter=2,
            year=2024,
            cpo=self.cpo,
        )

        ElecMeterReadingApplication.objects.create(
            status=ElecMeterReadingApplication.PENDING,
            quarter=3,
            year=2024,
            cpo=self.cpo,
        )

        self.meter_reading_2 = ElecMeterReading.objects.create(
            extracted_energy=800,
            renewable_energy=24.92,
            reading_date=datetime.date(2024, 6, 21),
            meter=self.meter2,
            cpo=self.cpo,
            application=self.meter_reading_application,
        )

        self.meter_reading_3 = ElecMeterReading.objects.create(
            extracted_energy=4,
            renewable_energy=2,
            reading_date=datetime.date(2024, 6, 29),
            meter=self.meter3,
            cpo=self.cpo,
            application=self.meter_reading_application,
        )

    def test_application_template(self):
        response = self.client.get(
            reverse("elec-cpo-meter-readings-get-application-template"),
            {"entity_id": self.cpo.id, "quarter": 3, "year": 2024},
        )

        assert response.status_code == 200

        file = io.BytesIO(response.content)
        workbook = openpyxl.load_workbook(file)
        sheet = workbook.active

        assert sheet["A2"].value == self.charge_point_1.charge_point_id
        assert sheet["B2"].value == self.charge_point_1.measure_energy
        assert sheet["C2"].value is None
        assert sheet["D2"].value is None

        assert sheet["A3"].value == self.charge_point_2.charge_point_id
        assert sheet["B3"].value == self.meter_reading_2.extracted_energy
        assert sheet["C3"].value is None
        assert sheet["D3"].value is None

        assert sheet["A4"].value == self.charge_point_4.charge_point_id
        assert sheet["B4"].value == self.meter4.initial_index
        assert sheet["C4"].value is None
        assert sheet["D4"].value is None

        assert sheet["A5"].value == self.charge_point_5.charge_point_id
        assert sheet["A6"].value == self.charge_point_6.charge_point_id
        assert sheet["A7"].value == self.charge_point_7.charge_point_id
        assert sheet["A8"].value == self.charge_point_8.charge_point_id
        assert sheet["A9"].value == self.charge_point_9.charge_point_id

        assert sheet["A10"].value is None

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
                "year": 2025,
                "file": SimpleUploadedFile("readings.xlsx", excel_file.read()),
            },
        )

        data = response.json()
        assert response.status_code == 400

        assert data == {
            "status": "error",
            "error": "VALIDATION_FAILED",
            "data": {
                "file_name": "readings.xlsx",
                "meter_reading_count": 1,
                "quarter": 3,
                "year": 2025,
                "error_count": 10,
                "errors": [
                    {
                        "error": "INVALID_DATA",
                        "line": 3,
                        "meta": {"extracted_energy": ["La quantité d'énergie soutirée est inférieure au précédent relevé."]},
                    },
                    {
                        "error": "INVALID_DATA",
                        "line": 4,
                        "meta": {"charge_point_id": ["Ce point de recharge a été défini 2 fois (lignes 4, 5)"]},
                    },
                    {
                        "error": "INVALID_DATA",
                        "line": 5,
                        "meta": {"charge_point_id": ["Ce point de recharge a été défini 2 fois (lignes 4, 5)"]},
                    },
                    {
                        "error": "INVALID_DATA",
                        "line": 6,
                        "meta": {"charge_point_id": ["Le point de recharge n'a pas encore été inscrit sur la plateforme."]},
                    },
                    {
                        "error": "INVALID_DATA",
                        "line": 7,
                        "meta": {"reading_date": ["La date du relevé ne correspond pas au trimestre traité actuellement."]},
                    },
                    {
                        "error": "INVALID_DATA",
                        "line": 8,
                        "meta": {
                            "charge_point_id": [
                                "Ce point de recharge n'a pas de compteur associé, veuillez en ajouter un depuis la page dédiée."  # noqa
                            ]
                        },
                    },
                    {
                        "error": "INVALID_DATA",
                        "line": 9,
                        "meta": {
                            "reading_date": [
                                "Un relevé plus récent est déjà enregistré pour ce point de recharge: 500.0kWh, 28/03/2024",
                                "La date du relevé ne correspond pas au trimestre traité actuellement.",
                            ],
                        },
                    },
                    {
                        "error": "INVALID_DATA",
                        "line": 10,
                        "meta": {
                            "extracted_energy": [
                                "Le facteur de charge estimé depuis le dernier relevé enregistré est supérieur à 100%. Veuillez vérifier les valeurs du relevé ainsi que la puissance de votre point de recharge, renseignée sur TDG."  # noqa
                            ],
                        },
                    },
                    {
                        "error": "INVALID_DATA",
                        "line": 11,
                        "meta": {
                            "reading_date": [
                                "La date du relevé ne correspond pas au trimestre traité actuellement.",
                            ],
                        },
                    },
                    {
                        "error": "INVALID_DATA",
                        "line": 12,
                        "meta": {
                            "reading_date": [
                                "La date du relevé ne correspond pas au trimestre traité actuellement.",
                            ],
                        },
                    },
                ],
            },
        }

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
                "year": 2025,
                "file": SimpleUploadedFile("readings.xlsx", excel_file.read()),
            },
        )

        data = response.json()
        assert response.status_code == 200
        assert data == {
            "status": "success",
            "data": {
                "file_name": "readings.xlsx",
                "meter_reading_count": 2,
                "quarter": 3,
                "year": 2025,
                "errors": [],
                "error_count": 0,
            },
        }

    def test_add_application_error(self):
        excel_file = create_meter_readings_excel(
            name="readings",
            quarter=3,
            year=2025,
            meter_readings_data=ERROR_METER_READINGS,
        )

        response = self.client.post(
            reverse("elec-cpo-meter-readings-add-application"),
            {
                "entity_id": self.cpo.id,
                "quarter": 3,
                "year": 2025,
                "file": SimpleUploadedFile("readings.xlsx", excel_file.read()),
            },
        )

        data = response.json()
        assert response.status_code == 400
        assert data == {"status": "error", "error": "VALIDATION_FAILED"}

    def test_add_application_ok(self):
        excel_file = create_meter_readings_excel(
            name="readings",
            quarter=3,
            year=2025,
            meter_readings_data=OK_METER_READINGS,
        )

        response = self.client.post(
            reverse("elec-cpo-meter-readings-add-application"),
            {
                "entity_id": self.cpo.id,
                "quarter": 3,
                "year": 2025,
                "file": SimpleUploadedFile("readings.xlsx", excel_file.read()),
            },
        )

        data = response.json()

        assert response.status_code == 200
        assert data == {"status": "success"}

        last_application = ElecMeterReadingApplication.objects.last()

        assert last_application.quarter == 3
        assert last_application.year == 2025
        assert last_application.elec_meter_readings.count() == 2

        readings = last_application.elec_meter_readings.all()
        reading_1 = readings[0]
        reading_2 = readings[1]

        assert reading_1.extracted_energy == 1100
        assert reading_1.reading_date == datetime.date(2025, 9, 25)
        assert reading_2.extracted_energy == 800
        assert reading_2.reading_date == datetime.date(2025, 9, 28)

    def test_get_applications(self):
        mocked_get_application_quarter = patch(
            "elec.services.meter_readings_application_quarter.get_application_quarter"
        ).start()
        mocked_get_application_quarter.return_value = (2024, 3)

        mocked_get_application_deadline = patch(
            "elec.services.meter_readings_application_quarter.get_application_deadline"
        ).start()
        mocked_get_application_deadline.return_value = (
            datetime.date(2024, 10, 15),
            "HIGH",
        )

        response = self.client.get(
            reverse("elec-cpo-meter-readings-get-applications"),
            {"entity_id": self.cpo.id},
        )

        application = ElecMeterReadingApplication.objects.last()

        data = response.json()
        assert response.status_code == 200

        expected = {
            "data": {
                "applications": [
                    {
                        "application_date": mock.ANY,
                        "charge_point_count": 2,
                        "cpo": {
                            "entity_type": "Charge Point Operator",
                            "id": self.cpo.id,
                            "name": "CPO",
                        },
                        "energy_total": 26.92,
                        "id": mock.ANY,
                        "quarter": 2,
                        "status": "ACCEPTED",
                        "year": 2024,
                    },
                    {
                        "application_date": mock.ANY,
                        "charge_point_count": 0,
                        "cpo": {
                            "entity_type": "Charge Point Operator",
                            "id": self.cpo.id,
                            "name": "CPO",
                        },
                        "energy_total": 0,
                        "id": application.id,
                        "quarter": 3,
                        "status": "PENDING",
                        "year": 2024,
                    },
                ],
                "current_application": mock.ANY,
                "current_application_period": {
                    "deadline": "2024-10-15",
                    "quarter": 3,
                    "urgency_status": "HIGH",
                    "year": 2024,
                    "charge_point_count": 8,
                },
            },
            "status": "success",
        }

        assert data == expected

        # With year filter
        response = self.client.get(
            reverse("elec-cpo-meter-readings-get-applications"),
            {"entity_id": self.cpo.id, "year": 2023},
        )
        data = response.json()
        assert response.status_code == 200
        assert len(data["data"]["applications"]) == 0

        response = self.client.get(
            reverse("elec-cpo-meter-readings-get-applications"),
            {"entity_id": self.cpo.id, "year": datetime.date.today().year},
        )
        data = response.json()
        assert response.status_code == 200
        assert len(data["data"]["applications"]) == 2
        assert data["data"]["applications"][0]["year"] == 2024

        # With status
        response = self.client.get(
            reverse("elec-cpo-meter-readings-get-applications"),
            {"entity_id": self.cpo.id, "status": "AUDIT_DONE"},
        )
        data = response.json()
        assert response.status_code == 200
        assert len(data["data"]["applications"]) == 0

        response = self.client.get(
            reverse("elec-cpo-meter-readings-get-applications"),
            {"entity_id": self.cpo.id, "status": "PENDING"},
        )
        data = response.json()
        assert response.status_code == 200
        assert len(data["data"]["applications"]) == 1
        assert data["data"]["applications"][0]["status"] == "PENDING"

        # With pagination
        response = self.client.get(
            reverse("elec-cpo-meter-readings-get-applications"),
            {"entity_id": self.cpo.id, "from_idx": 0, "limit": 1},
        )
        data = response.json()
        assert response.status_code == 200
        assert len(data["data"]["applications"]) == 1

    def test_get_application_details(self):
        response = self.client.get(
            reverse("elec-cpo-meter-readings-get-application-details"),
            {
                "entity_id": self.cpo.id,
                "application_id": self.meter_reading_application.id,
            },
        )

        data = response.json()

        assert response.status_code == 200
        assert data == {
            "status": "success",
            "data": [
                {
                    "charge_point_id": "FR00EFGH",
                    "previous_reading": 700.0,
                    "current_reading": 800.0,
                    "reading_date": "2024-06-21",
                },
                {
                    "charge_point_id": "FR00IJKL",
                    "previous_reading": 500.0,
                    "current_reading": 4.0,
                    "reading_date": "2024-06-29",
                },
            ],
        }

    def test_delete_application_ok(self):
        assert ElecMeterReadingApplication.objects.count() > 1
        application = ElecMeterReadingApplication.objects.filter(status=ElecMeterReadingApplication.ACCEPTED).first()
        application_id = application.id
        meter_readings = ElecMeterReading.objects.filter(application=application)
        assert meter_readings.count() > 0

        application.status = ElecMeterReadingApplication.PENDING
        application.save()

        assert application.status == ElecMeterReadingApplication.PENDING
        response = self.client.post(
            reverse("elec-cpo-meter-readings-delete-application"),
            {"entity_id": self.cpo.id, "id": application.id},
        )

        data = response.json()

        assert response.status_code == 200
        assert data == {"status": "success"}

        assert not ElecMeterReadingApplication.objects.filter(id=application_id).exists()
        assert not ElecMeterReading.objects.filter(application_id=application_id).exists()

    def test_delete_application_nok(self):
        assert ElecMeterReadingApplication.objects.count() > 1
        application = ElecMeterReadingApplication.objects.filter(status=ElecMeterReadingApplication.ACCEPTED).first()
        application_id = application.id
        meter_readings = ElecMeterReading.objects.filter(application=application)
        assert meter_readings.count() > 0

        assert application.status == ElecMeterReadingApplication.ACCEPTED
        response = self.client.post(
            reverse("elec-cpo-meter-readings-delete-application"),
            {"entity_id": self.cpo.id, "id": application.id},
        )

        data = response.json()

        assert response.status_code == 400
        assert data == {"status": "error", "error": "APPLICATION_NOT_PENDING"}
        assert "error" in data
        assert data["error"] == "APPLICATION_NOT_PENDING"
        assert ElecMeterReadingApplication.objects.filter(id=application_id).exists()
        assert ElecMeterReading.objects.filter(application_id=application_id).exists()

    def test_facteur_de_charge(self):
        excel_file = create_meter_readings_excel(
            name="readings",
            quarter=4,
            year=2024,
            meter_readings_data=[
                # first reading for this PDC since registration (previous data from meter)
                {
                    "charge_point_id": "FR00ABCD",
                    "previous_reading": 1000,
                    "current_reading": 1100,  # delta = 100
                    "reading_date": datetime.date(2024, 12, 25),  # previous = 2024-03-30, delta = 270
                },
                # second reading for this PDC since registration (previous data from last meter reading)
                {
                    "charge_point_id": "FR00EFGH",
                    "previous_reading": 800,
                    "current_reading": 1000,  # delta = 200
                    "reading_date": datetime.date(2024, 12, 28),  # previous = 2024-06-21, delta = 190
                },
            ],
        )

        response = self.client.post(
            reverse("elec-cpo-meter-readings-add-application"),
            {
                "entity_id": self.cpo.id,
                "quarter": 4,
                "year": 2024,
                "file": SimpleUploadedFile("readings.xlsx", excel_file.read()),
            },
        )

        data = response.json()

        assert response.status_code == 200
        assert data == {"status": "success"}

        last_application = ElecMeterReadingApplication.objects.last()

        assert last_application.quarter == 4
        assert last_application.year == 2024
        assert last_application.elec_meter_readings.count() == 2

        readings = last_application.elec_meter_readings.all()
        reading_1 = readings[0]
        reading_2 = readings[1]

        assert reading_1.energy_used_since_last_reading == 100
        assert reading_1.days_since_last_reading == 270
        assert round(reading_1.facteur_de_charge, 6) == 0.001543
        assert reading_2.energy_used_since_last_reading == 200
        assert reading_2.days_since_last_reading == 190
        assert round(reading_2.facteur_de_charge, 6) == 0.000877
