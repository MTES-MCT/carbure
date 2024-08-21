import datetime
import os
from decimal import Decimal
from unittest.mock import patch

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


class ElecCharginPointsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # mock call to TransportDataGouv not to depend on the dynamic CSV and have predictable "allowed" charge points
        cls.mocked_download_csv = patch("elec.services.transport_data_gouv.TransportDataGouv.download_csv").start()
        cls.mocked_download_csv.return_value = "%s/web/elec/fixtures/transport_data_gouv.csv" % (os.environ["CARBURE_HOME"])

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls.mocked_download_csv.stop()

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

        self.meter = ElecMeter.objects.create(
            mid_certificate="123-456",
            initial_index=1000.1234,
            initial_index_date=datetime.date(2023, 6, 29),
            charge_point=None,
        )

    def test_check_charge_point_wrong_entity(self):
        filepath = "%s/web/elec/fixtures/full_ac_charge_points_error.xlsx" % (os.environ["CARBURE_HOME"])

        with open(filepath, "rb") as reader:
            file = SimpleUploadedFile("full_ac_charge_points_error.xlsx", reader.read())

        response = self.client.post(
            reverse("elec-cpo-charge-points-check-application"),
            {"entity_id": self.operator.id, "file": file},
        )

        data = response.json()
        assert response.status_code == 403
        assert data["error"] == "WRONG_ENTITY_TYPE"

    def test_check_full_ac_charge_point_errors(self):
        application = ElecChargePointApplication.objects.create(cpo=self.cpo)
        application.created_at = datetime.date(2023, 12, 28)
        application.save()

        ElecChargePoint.objects.create(
            application=application,
            cpo=self.cpo,
            charge_point_id="FRBBBB222203",
            current_type="AC",
            installation_date=datetime.date(2023, 2, 15),
            measure_reference_point_id="123456",
            station_name="Station",
            station_id="FGHIJ",
            nominal_power=150,
        )

        filepath = "%s/web/elec/fixtures/full_ac_charge_points_error.xlsx" % (os.environ["CARBURE_HOME"])

        with open(filepath, "rb") as reader:
            file = SimpleUploadedFile("full_ac_charge_points_error.xlsx", reader.read())

        response = self.client.post(
            reverse("elec-cpo-charge-points-check-application"),
            {"entity_id": self.cpo.id, "file": file},
        )

        expected = {
            "status": "error",
            "data": {
                "file_name": "full_ac_charge_points_error.xlsx",
                "charge_point_count": 0,
                "errors": [
                    {
                        "error": "INVALID_DATA",
                        "line": 35,
                        "meta": {
                            "installation_date": ["Saisissez une date valide."],
                        },
                    },
                    {
                        "error": "INVALID_DATA",
                        "line": 36,
                        "meta": {
                            "measure_date": [
                                "Saisissez une date valide.",
                                "La date du dernier relevé est obligatoire.",
                            ],
                        },
                    },
                    {
                        "error": "INVALID_DATA",
                        "line": 37,
                        "meta": {
                            "measure_energy": [
                                "Saisissez un nombre.",
                                "L'énergie mesurée lors du dernier relevé est obligatoire.",
                            ],
                        },
                    },
                    {
                        "error": "INVALID_DATA",
                        "line": 38,
                        "meta": {
                            "charge_point_id": [
                                "Le point de recharge FRBBBB222205 n'est pas listé dans les données consolidées de transport.data.gouv.fr"  # noqa: E501
                            ]
                        },
                    },
                    {
                        "error": "INVALID_DATA",
                        "line": 39,
                        "meta": {
                            "charge_point_id": [
                                "Le point de recharge FRBBBB222206 n'est pas listé dans les données consolidées de transport.data.gouv.fr"  # noqa: E501
                            ]
                        },
                    },
                    {
                        "error": "INVALID_DATA",
                        "line": 40,
                        "meta": {
                            "charge_point_id": [
                                "Le point de recharge FRBBBB222207 n'est pas listé dans les données consolidées de transport.data.gouv.fr"  # noqa: E501
                            ]
                        },
                    },
                    {
                        "error": "INVALID_DATA",
                        "line": 41,
                        "meta": {"charge_point_id": ["Le point de recharge FRBBBB222203 existe déjà"]},
                    },
                ],
                "error_count": 7,
            },
            "error": "VALIDATION_FAILED",
        }

        assert response.status_code == 400
        assert response.json() == expected

    def test_check_full_ac_charge_point_ok(self):
        filepath = "%s/web/elec/fixtures/full_ac_charge_points_ok.xlsx" % (os.environ["CARBURE_HOME"])

        with open(filepath, "rb") as reader:
            file = SimpleUploadedFile("full_ac_charge_points_ok.xlsx", reader.read())

        response = self.client.post(
            reverse("elec-cpo-charge-points-check-application"),
            {"entity_id": self.cpo.id, "file": file},
        )

        expected = {
            "status": "success",
            "data": {
                "file_name": "full_ac_charge_points_ok.xlsx",
                "charge_point_count": 6,
                "errors": [],
                "error_count": 0,
            },
        }

        assert response.json() == expected
        assert response.status_code == 200

    def test_add_full_ac_charge_point_errors(self):
        filepath = "%s/web/elec/fixtures/full_ac_charge_points_error.xlsx" % (os.environ["CARBURE_HOME"])

        with open(filepath, "rb") as reader:
            file = SimpleUploadedFile("full_ac_charge_points_error.xlsx", reader.read())

        response = self.client.post(
            reverse("elec-cpo-charge-points-add-application"),
            {"entity_id": self.cpo.id, "file": file},
        )

        assert response.status_code == 400
        assert response.json() == {"status": "error", "error": "VALIDATION_FAILED"}

    def test_add_full_ac_charge_point_ok(self):
        filepath = "%s/web/elec/fixtures/full_ac_charge_points_ok.xlsx" % (os.environ["CARBURE_HOME"])

        with open(filepath, "rb") as reader:
            file = SimpleUploadedFile("full_ac_charge_points_ok.xlsx", reader.read())

        assert ElecChargePointApplication.objects.count() == 0
        assert ElecChargePoint.objects.count() == 0

        response = self.client.post(
            reverse("elec-cpo-charge-points-add-application"),
            {"entity_id": self.cpo.id, "file": file},
        )

        assert response.status_code == 200
        assert response.json() == {"status": "success"}

        applications = ElecChargePointApplication.objects.all()
        application = applications.first()
        charge_points = application.elec_charge_points.all()

        assert applications.count() == 1
        assert charge_points.count() == 6

        assert charge_points[0].charge_point_id == "FRAAAA111101"
        assert charge_points[0].current_type == "AC"
        assert str(charge_points[0].installation_date) == "2022-05-10"
        assert charge_points[0].mid_id == "1234561"
        assert str(charge_points[0].measure_date) == "2023-12-29"
        assert charge_points[0].measure_energy == 1000.0
        assert charge_points[0].is_article_2 is False
        assert charge_points[0].measure_reference_point_id == ""
        assert charge_points[0].cpo == self.cpo
        assert charge_points[0].application == application
        assert charge_points[0].station_id == "FRAAAA1111"
        assert charge_points[0].station_name == "Hotel Saint Sauveur"
        assert charge_points[0].nominal_power == 22
        assert charge_points[0].latitude == Decimal("43.41959147913006")
        assert charge_points[0].longitude == Decimal("3.407609123225763")

        assert charge_points[1].charge_point_id == "FRAAAA111102"
        assert charge_points[1].current_type == "AC"
        assert charge_points[1].is_article_2 is False
        assert charge_points[1].station_id == "FRAAAA1111"

        assert charge_points[2].charge_point_id == "FRAAAA111103"
        assert charge_points[2].current_type == "AC"
        assert charge_points[2].is_article_2 is False
        assert charge_points[2].station_id == "FRAAAA1111"

        assert charge_points[3].charge_point_id == "FRBBBB222201"
        assert charge_points[3].current_type == "DC"
        assert charge_points[3].is_article_2 is False
        assert charge_points[3].station_id == "FRBBBB2222"

        assert charge_points[4].charge_point_id == "FRBBBB222202"
        assert charge_points[4].current_type == "DC"
        assert charge_points[4].is_article_2 is False
        assert charge_points[4].station_id == "FRBBBB2222"

        assert charge_points[5].charge_point_id == "FRBBBB222203"
        assert charge_points[5].current_type == "AC"
        assert charge_points[5].is_article_2 is False
        assert charge_points[5].station_id == "FRBBBB2222"

    def test_add_partial_dc_charge_point_ok(self):
        filepath = "%s/web/elec/fixtures/partial_dc_charge_points_ok.xlsx" % (os.environ["CARBURE_HOME"])

        with open(filepath, "rb") as reader:
            file = SimpleUploadedFile("partial_dc_charge_points_ok.xlsx", reader.read())

        assert ElecChargePointApplication.objects.count() == 0
        assert ElecChargePoint.objects.count() == 0

        response = self.client.post(
            reverse("elec-cpo-charge-points-add-application"),
            {"entity_id": self.cpo.id, "file": file},
        )

        assert response.status_code == 200
        assert response.json() == {"status": "success"}

        applications = ElecChargePointApplication.objects.all()
        application = applications.first()
        charge_points = application.elec_charge_points.all()

        assert applications.count() == 1
        assert charge_points.count() == 5

        assert charge_points[0].charge_point_id == "FRBBBB222201"
        assert charge_points[0].current_type == "DC"
        assert str(charge_points[0].installation_date) == "2022-05-10"
        assert charge_points[0].mid_id == ""
        assert charge_points[0].measure_date is None
        assert charge_points[0].measure_energy == 0
        assert charge_points[0].is_article_2 is True
        assert charge_points[0].measure_reference_point_id == "1234561"
        assert charge_points[0].cpo == self.cpo
        assert charge_points[0].application == application
        assert charge_points[0].station_id == "FRBBBB2222"
        assert charge_points[0].station_name == "Carry-le-Merle"
        assert charge_points[0].nominal_power == 36.0
        assert charge_points[0].latitude == Decimal("43.3292004491334")
        assert charge_points[0].longitude == Decimal("5.143766265497639")

        assert charge_points[1].charge_point_id == "FRBBBB222202"
        assert charge_points[1].current_type == "DC"
        assert charge_points[1].is_article_2 is True
        assert charge_points[1].station_id == "FRBBBB2222"

        assert charge_points[2].charge_point_id == "FRBBBB222203"
        assert charge_points[2].current_type == "AC"
        assert charge_points[2].is_article_2 is True
        assert charge_points[2].station_id == "FRBBBB2222"

        assert charge_points[3].charge_point_id == "FRCCCC333301"
        assert charge_points[3].current_type == "DC"
        assert charge_points[3].is_article_2 is True
        assert charge_points[3].station_id == "FRCCCC3333"

        assert charge_points[4].charge_point_id == "FRCCCC333303"
        assert charge_points[4].current_type == "AC"
        assert charge_points[4].is_article_2 is True
        assert charge_points[4].station_id == "FRCCCC3333"

    def test_get_applications_ok(self):
        application = ElecChargePointApplication.objects.create(cpo=self.cpo)
        application.created_at = datetime.date(2023, 12, 28)
        application.save()

        application2 = ElecChargePointApplication.objects.create(cpo=self.cpo)
        application2.created_at = datetime.date(2023, 12, 29)
        application2.save()

        application3 = ElecChargePointApplication.objects.create(cpo=self.cpo)
        application3.created_at = datetime.date(2024, 12, 29)
        application3.status = "ACCEPTED"
        application3.save()

        ElecChargePoint.objects.create(
            application=application,
            cpo=self.cpo,
            charge_point_id="ABCDE",
            current_type="AC",
            installation_date=datetime.date(2023, 2, 15),
            current_meter=self.meter,
            measure_reference_point_id="123456",
            station_name="Station",
            station_id="FGHIJ",
            nominal_power=150,
        )

        ElecChargePoint.objects.create(
            application=application2,
            cpo=self.cpo,
            charge_point_id="BCDEF",
            current_type="AC",
            installation_date=datetime.date(2023, 2, 15),
            current_meter=self.meter,
            measure_reference_point_id="123456",
            station_name="Station",
            station_id="FGHIJ",
            nominal_power=40,
        )

        response = self.client.get(
            reverse("elec-cpo-charge-points-get-applications"),
            {"entity_id": self.cpo.id},
        )

        data = response.json()

        cpo = {"id": self.cpo.id, "entity_type": self.cpo.entity_type, "name": self.cpo.name}

        expected = {
            "status": "success",
            "data": [
                {
                    "id": application.id,
                    "cpo": cpo,
                    "status": "PENDING",
                    "application_date": "2023-12-28",
                    "station_count": 1,
                    "charge_point_count": 1,
                    "power_total": 150,
                },
                {
                    "id": application2.id,
                    "cpo": cpo,
                    "status": "PENDING",
                    "application_date": "2023-12-29",
                    "station_count": 1,
                    "charge_point_count": 1,
                    "power_total": 40,
                },
                {
                    "id": application3.id,
                    "cpo": cpo,
                    "status": "ACCEPTED",
                    "application_date": "2024-12-29",
                    "station_count": 0,
                    "charge_point_count": 0,
                    "power_total": 0,
                },
            ],
        }

        assert response.status_code == 200
        assert data == expected

        # With year filter
        response = self.client.get(
            reverse("elec-cpo-charge-points-get-applications"),
            {"entity_id": self.cpo.id, "year": 2023},
        )
        data = response.json()
        assert response.status_code == 200
        assert len(data["data"]) == 2

        response = self.client.get(
            reverse("elec-cpo-charge-points-get-applications"),
            {"entity_id": self.cpo.id, "year": 2024},
        )
        data = response.json()
        assert response.status_code == 200
        assert len(data["data"]) == 1
        assert data["data"][0]["application_date"] == "2024-12-29"

        # With status
        response = self.client.get(
            reverse("elec-cpo-charge-points-get-applications"),
            {"entity_id": self.cpo.id, "status": "AUDIT_DONE"},
        )
        data = response.json()
        assert response.status_code == 200
        assert len(data["data"]) == 0

        response = self.client.get(
            reverse("elec-cpo-charge-points-get-applications"),
            {"entity_id": self.cpo.id, "status": "PENDING"},
        )
        data = response.json()
        assert response.status_code == 200
        assert len(data["data"]) == 2
        assert data["data"][0]["status"] == "PENDING"

        # With pagination
        response = self.client.get(
            reverse("elec-cpo-charge-points-get-applications"),
            {"entity_id": self.cpo.id, "from_idx": 0, "limit": 1},
        )
        data = response.json()
        assert response.status_code == 200
        assert len(data["data"]) == 1

    def test_get_charge_points_ok(self):
        application = ElecChargePointApplication.objects.create(cpo=self.cpo)
        application.created_at = datetime.date(2023, 1, 5)
        application.save()
        application2 = ElecChargePointApplication.objects.create(cpo=self.cpo)
        application2.created_at = datetime.date(2023, 1, 6)
        application2.save()

        charge_point = ElecChargePoint.objects.create(
            application=application,
            cpo=self.cpo,
            charge_point_id="ABCDE",
            current_type="AC",
            installation_date=datetime.date(2023, 2, 15),
            current_meter=self.meter,
            measure_reference_point_id="123456",
            station_name="Station",
            station_id="FGHIJ",
            nominal_power=150,
            cpo_name="Alice",
            cpo_siren="12345",
        )

        charge_point2 = ElecChargePoint.objects.create(
            application=application2,
            cpo=self.cpo,
            charge_point_id="BCDEF",
            current_type="AC",
            installation_date=datetime.date(2023, 2, 15),
            current_meter=self.meter,
            measure_reference_point_id="123456",
            station_name="Station",
            station_id="FGHIJ",
            nominal_power=40,
            cpo_name="Bob",
            cpo_siren="67890",
        )

        meter_reading_application = ElecMeterReadingApplication.objects.create(
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

        ElecMeterReading.objects.create(
            extracted_energy=40,
            renewable_energy=20,
            reading_date=datetime.date(2024, 9, 30),
            cpo=self.cpo,
            application=meter_reading_application,
        )

        ElecMeterReading.objects.create(
            extracted_energy=4,
            renewable_energy=2,
            reading_date=datetime.date(2024, 9, 29),
            cpo=self.cpo,
            application=meter_reading_application,
        )

        response = self.client.get(
            reverse("elec-cpo-charge-points-get-charge-points"),
            {"entity_id": self.cpo.id},
        )

        expected = {
            "status": "success",
            "data": [
                {
                    "id": charge_point.id,
                    "cpo": self.cpo.name,
                    "charge_point_id": "ABCDE",
                    "current_type": "AC",
                    "installation_date": "2023-02-15",
                    "mid_id": "123-456",
                    "measure_date": "2023-06-29",
                    "measure_energy": 1000.123,
                    "is_article_2": False,
                    "measure_reference_point_id": "123456",
                    "station_name": "Station",
                    "station_id": "FGHIJ",
                    "nominal_power": 150.0,
                    "cpo_name": "Alice",
                    "cpo_siren": "12345",
                    "status": "PENDING",
                },
                {
                    "id": charge_point2.id,
                    "cpo": self.cpo.name,
                    "charge_point_id": "BCDEF",
                    "current_type": "AC",
                    "installation_date": "2023-02-15",
                    "mid_id": "123-456",
                    "measure_date": "2023-06-29",
                    "measure_energy": 1000.123,
                    "is_article_2": False,
                    "measure_reference_point_id": "123456",
                    "station_name": "Station",
                    "station_id": "FGHIJ",
                    "nominal_power": 40.0,
                    "cpo_name": "Bob",
                    "cpo_siren": "67890",
                    "status": "PENDING",
                },
            ],
        }

        data = response.json()
        assert response.status_code == 200
        assert data == expected

        # With year filter
        response = self.client.get(
            reverse("elec-cpo-charge-points-get-charge-points"),
            {"entity_id": self.cpo.id, "year": 2022},
        )
        data = response.json()
        assert response.status_code == 200
        assert len(data["data"]) == 0

        response = self.client.get(
            reverse("elec-cpo-charge-points-get-charge-points"),
            {"entity_id": self.cpo.id, "year": 2023},
        )
        data = response.json()
        assert response.status_code == 200
        assert len(data["data"]) == 2
        assert ElecChargePoint.objects.get(id=data["data"][0]["id"]).application.created_at.year == 2023

        # With status
        response = self.client.get(
            reverse("elec-cpo-charge-points-get-charge-points"),
            {"entity_id": self.cpo.id, "status": "AUDIT_DONE"},
        )
        data = response.json()
        assert response.status_code == 200
        assert len(data["data"]) == 0

        response = self.client.get(
            reverse("elec-cpo-charge-points-get-charge-points"),
            {"entity_id": self.cpo.id, "status": "PENDING"},
        )
        data = response.json()
        assert response.status_code == 200
        assert len(data["data"]) == 2
        assert ElecChargePoint.objects.get(id=data["data"][0]["id"]).application.status == "PENDING"

        # With created_at filter
        response = self.client.get(
            reverse("elec-cpo-charge-points-get-charge-points"),
            {"entity_id": self.cpo.id, "created_at": "2023-01-04"},
        )
        data = response.json()
        assert response.status_code == 200
        assert len(data["data"]) == 0

        response = self.client.get(
            reverse("elec-cpo-charge-points-get-charge-points"),
            {"entity_id": self.cpo.id, "created_at": "2023-01-05"},
        )
        data = response.json()
        assert response.status_code == 200
        assert len(data["data"]) == 1
        assert ElecChargePoint.objects.get(id=data["data"][0]["id"]).application.created_at == datetime.date(2023, 1, 5)

        # With charge_point_id filter
        response = self.client.get(
            reverse("elec-cpo-charge-points-get-charge-points"),
            {"entity_id": self.cpo.id, "charge_point_id": "AAAAA"},
        )
        data = response.json()
        assert response.status_code == 200
        assert len(data["data"]) == 0

        response = self.client.get(
            reverse("elec-cpo-charge-points-get-charge-points"),
            {"entity_id": self.cpo.id, "charge_point_id": "ABCDE"},
        )
        data = response.json()
        assert response.status_code == 200
        assert len(data["data"]) == 1
        assert data["data"][0]["charge_point_id"] == "ABCDE"

        # With last_extracted_energy filter
        # response = self.client.get(
        #     reverse("elec-cpo-charge-points-get-charge-points"),
        #     {"entity_id": self.cpo.id, "last_extracted_energy": "4"},
        # )
        # data = response.json()
        # self.assertEqual(response.status_code, 200)
        # self.assertEqual(len(data["data"]), 0)

        # response = self.client.get(
        #     reverse("elec-cpo-charge-points-get-charge-points"),
        #     {"entity_id": self.cpo.id, "last_extracted_energy": "40"},
        # )
        # data = response.json()
        # self.assertEqual(response.status_code, 200)
        # self.assertEqual(len(data["data"]), 1)

        # With is_article_2 filter
        response = self.client.get(
            reverse("elec-cpo-charge-points-get-charge-points"),
            {"entity_id": self.cpo.id, "is_article_2": True},
        )
        data = response.json()
        assert response.status_code == 200
        assert len(data["data"]) == 0

        response = self.client.get(
            reverse("elec-cpo-charge-points-get-charge-points"),
            {"entity_id": self.cpo.id, "is_article_2": False},
        )
        data = response.json()
        assert response.status_code == 200
        assert len(data["data"]) == 2
        assert ElecChargePoint.objects.get(id=data["data"][0]["id"]).is_article_2 is False

        # With pagination
        response = self.client.get(
            reverse("elec-cpo-charge-points-get-charge-points"),
            {"entity_id": self.cpo.id, "from_idx": 0, "limit": 1},
        )
        data = response.json()
        assert response.status_code == 200
        assert len(data["data"]) == 1

    def test_get_application_details_ok(self):
        application = ElecChargePointApplication.objects.create(cpo=self.cpo)
        application2 = ElecChargePointApplication.objects.create(cpo=self.cpo)

        charge_point = ElecChargePoint.objects.create(
            application=application,
            cpo=self.cpo,
            charge_point_id="ABCDE",
            current_type="AC",
            installation_date=datetime.date(2023, 2, 15),
            current_meter=self.meter,
            measure_reference_point_id="123456",
            station_name="Station",
            station_id="FGHIJ",
            nominal_power=150,
            cpo_name="Alice",
            cpo_siren="12345",
        )

        ElecChargePoint.objects.create(
            application=application2,
            cpo=self.cpo,
            charge_point_id="ABCDE",
            current_type="AC",
            installation_date=datetime.date(2023, 2, 15),
            current_meter=self.meter,
            measure_reference_point_id="123456",
            station_name="Station",
            station_id="FGHIJ",
            nominal_power=40,
            cpo_name="Bob",
            cpo_siren="67890",
        )

        response = self.client.get(
            reverse("elec-cpo-charge-points-get-application-details"),
            {"entity_id": self.cpo.id, "application_id": application.id},
        )

        expected = {
            "status": "success",
            "data": [
                {
                    "id": charge_point.id,
                    "cpo": self.cpo.name,
                    "charge_point_id": "ABCDE",
                    "current_type": "AC",
                    "installation_date": "2023-02-15",
                    "mid_id": "123-456",
                    "measure_date": "2023-06-29",
                    "measure_energy": 1000.123,
                    "is_article_2": False,
                    "measure_reference_point_id": "123456",
                    "station_name": "Station",
                    "station_id": "FGHIJ",
                    "nominal_power": 150.0,
                    "cpo_name": "Alice",
                    "cpo_siren": "12345",
                    "status": "PENDING",
                }
            ],
        }

        data = response.json()
        assert response.status_code == 200
        assert data == expected
