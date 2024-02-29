import os
import datetime
from decimal import Decimal
from unittest.mock import patch
from django.test import TestCase
from django.urls import reverse

from core.tests_utils import setup_current_user
from core.models import Entity
from django.core.files.uploadedfile import SimpleUploadedFile
from elec.models.elec_charge_point import ElecChargePoint
from elec.models.elec_charge_point_application import ElecChargePointApplication


class ElecCharginPointsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # mock call to TransportDataGouv not to depend on the dynamic CSV and have predictable "allowed" charge points
        cls.mocked_find_charge_point_data = patch("elec.services.transport_data_gouv.TransportDataGouv.find_charge_point_data").start()  # fmt:skip

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls.mocked_find_charge_point_data.stop()

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

    def test_check_charge_point_wrong_entity(self):
        filepath = "%s/web/elec/fixtures/points-de-recharge-errors.xlsx" % (os.environ["CARBURE_HOME"])

        with open(filepath, "rb") as reader:
            file = SimpleUploadedFile("points-de-recharge-errors.xlsx", reader.read())

        response = self.client.post(
            reverse("elec-cpo-charge-points-check-application"),
            {"entity_id": self.operator.id, "file": file},
        )

        data = response.json()
        self.assertEqual(response.status_code, 403)
        self.assertEqual(data["error"], "WRONG_ENTITY_TYPE")

    def test_check_charge_point_errors(self):
        self.mocked_find_charge_point_data.return_value = TDG_MOCK_ERROR

        filepath = "%s/web/elec/fixtures/points-de-recharge-errors.xlsx" % (os.environ["CARBURE_HOME"])

        with open(filepath, "rb") as reader:
            file = SimpleUploadedFile("points-de-recharge-errors.xlsx", reader.read())

        response = self.client.post(
            reverse("elec-cpo-charge-points-check-application"),
            {"entity_id": self.cpo.id, "file": file},
        )

        expected = {
            "status": "error",
            "error": "VALIDATION_FAILED",
            "data": {
                "file_name": "points-de-recharge-errors.xlsx",
                "pending_application_already_exists": False,
                "charge_point_count": 0,
                "error_count": 5,
                "errors": [
                    {
                        "error": "INVALID_DATA",
                        "line": 35,
                        "meta": {
                            "measure_date": [
                                "Saisissez une date valide.",
                                "La date du dernier relevé est obligatoire.",
                            ],
                            "measure_energy": [
                                "Saisissez un nombre.",
                                "L'énergie mesurée lors du dernier relevé est obligatoire.",
                            ],
                        },
                    },
                    {
                        "error": "INVALID_DATA",
                        "line": 36,
                        "meta": {"charge_point_id": ["Ce point de recharge n'est pas listé sur transport.data.gouv.fr"]},
                    },
                    {
                        "error": "INVALID_DATA",
                        "line": 37,
                        "meta": {"charge_point_id": ["Ce point de recharge n'est pas listé sur transport.data.gouv.fr"]},
                    },
                    {
                        "error": "INVALID_DATA",
                        "line": 38,
                        "meta": {"charge_point_id": ["Ce point de recharge n'est pas listé sur transport.data.gouv.fr"]},
                    },
                    {
                        "error": "INVALID_DATA",
                        "line": 39,
                        "meta": {"charge_point_id": ["Ce point de recharge n'est pas listé sur transport.data.gouv.fr"]},
                    },
                ],
            },
        }

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), expected)

    def test_check_charge_point_ok(self):
        self.mocked_find_charge_point_data.return_value = TDG_MOCK_OK

        filepath = "%s/web/elec/fixtures/points-de-recharge-ok.xlsx" % (os.environ["CARBURE_HOME"])

        with open(filepath, "rb") as reader:
            file = SimpleUploadedFile("points-de-recharge-ok.xlsx", reader.read())

        response = self.client.post(
            reverse("elec-cpo-charge-points-check-application"),
            {"entity_id": self.cpo.id, "file": file},
        )

        expected = {
            "status": "success",
            "data": {
                "file_name": "points-de-recharge-ok.xlsx",
                "charge_point_count": 5,
                "errors": [],
                "error_count": 0,
                "pending_application_already_exists": False,
            },
        }

        self.assertEqual(response.json(), expected)
        self.assertEqual(response.status_code, 200)

    def test_add_charge_point_errors(self):
        self.mocked_find_charge_point_data.return_value = TDG_MOCK_ERROR

        filepath = "%s/web/elec/fixtures/points-de-recharge-errors.xlsx" % (os.environ["CARBURE_HOME"])

        with open(filepath, "rb") as reader:
            file = SimpleUploadedFile("points-de-recharge-errors.xlsx", reader.read())

        response = self.client.post(
            reverse("elec-cpo-charge-points-add-application"),
            {"entity_id": self.cpo.id, "file": file},
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"status": "error", "error": "VALIDATION_FAILED"})

    def test_add_charge_point_ok(self):
        self.mocked_find_charge_point_data.return_value = TDG_MOCK_OK

        filepath = "%s/web/elec/fixtures/points-de-recharge-ok.xlsx" % (os.environ["CARBURE_HOME"])

        with open(filepath, "rb") as reader:
            file = SimpleUploadedFile("points-de-recharge-ok.xlsx", reader.read())

        self.assertEqual(ElecChargePointApplication.objects.count(), 0)
        self.assertEqual(ElecChargePoint.objects.count(), 0)

        response = self.client.post(
            reverse("elec-cpo-charge-points-add-application"),
            {"entity_id": self.cpo.id, "file": file},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "success"})

        applications = ElecChargePointApplication.objects.all()
        application = applications.first()
        charge_points = application.elec_charge_points.all()

        self.assertEqual(applications.count(), 1)
        self.assertEqual(charge_points.count(), 5)

        self.assertEqual(charge_points[0].charge_point_id, "FR000011062174")
        self.assertEqual(charge_points[0].current_type, "AC")
        self.assertEqual(str(charge_points[0].installation_date), "2023-06-12")
        self.assertEqual(charge_points[0].mid_id, "123456-10")
        self.assertEqual(str(charge_points[0].measure_date), "2023-08-28")
        self.assertEqual(charge_points[0].measure_energy, 98765.430)
        self.assertEqual(charge_points[0].is_article_2, False)
        self.assertEqual(charge_points[0].measure_reference_point_id, "1122334455")
        self.assertEqual(charge_points[0].cpo, self.cpo)
        self.assertEqual(charge_points[0].application, application)
        self.assertEqual(charge_points[0].station_id, "FR000011062174")
        self.assertEqual(charge_points[0].station_name, "Hotel saint alban")
        self.assertEqual(charge_points[0].nominal_power, 22)
        self.assertEqual(charge_points[0].latitude, Decimal("43.419591"))
        self.assertEqual(charge_points[0].longitude, Decimal("3.407609"))

        self.assertEqual(charge_points[1].charge_point_id, "FR000012292701")
        self.assertEqual(charge_points[1].current_type, "AC")
        self.assertEqual(str(charge_points[1].installation_date), "2023-06-13")
        self.assertEqual(charge_points[1].mid_id, "123457-11")
        self.assertEqual(str(charge_points[1].measure_date), "2023-08-29")
        self.assertEqual(charge_points[1].measure_energy, 98765.430)
        self.assertEqual(charge_points[1].is_article_2, False)
        self.assertEqual(charge_points[1].measure_reference_point_id, "1122334456")
        self.assertEqual(charge_points[1].cpo, self.cpo)
        self.assertEqual(charge_points[1].application, application)
        self.assertEqual(charge_points[1].station_id, "FR000012292701")
        self.assertEqual(charge_points[1].station_name, "Hôtel Restaurant Campanile Nogent-sur-Marne")
        self.assertEqual(charge_points[1].nominal_power, 22)

        self.assertEqual(charge_points[2].charge_point_id, "FR000012308585")
        self.assertEqual(charge_points[2].current_type, "AC")
        self.assertEqual(str(charge_points[2].installation_date), "2023-06-14")
        self.assertEqual(charge_points[2].mid_id, "123458-12")
        self.assertEqual(str(charge_points[2].measure_date), "2023-08-30")
        self.assertEqual(charge_points[2].measure_energy, 98765.430)
        self.assertEqual(charge_points[2].is_article_2, False)
        self.assertEqual(charge_points[2].measure_reference_point_id, "1122334457")
        self.assertEqual(charge_points[2].cpo, self.cpo)
        self.assertEqual(charge_points[2].application, application)
        self.assertEqual(charge_points[2].station_id, "FR000012308585")
        self.assertEqual(charge_points[2].station_name, "Résidence les calanques")
        self.assertEqual(charge_points[2].nominal_power, 22)

        self.assertEqual(charge_points[3].charge_point_id, "FR000012616553")
        self.assertEqual(charge_points[3].current_type, "AC")
        self.assertEqual(str(charge_points[3].installation_date), "2023-06-15")
        self.assertEqual(charge_points[3].mid_id, "123459-13")
        self.assertEqual(str(charge_points[3].measure_date), "2023-08-31")
        self.assertEqual(charge_points[3].measure_energy, 98765.430)
        self.assertEqual(charge_points[3].is_article_2, False)
        self.assertEqual(charge_points[3].measure_reference_point_id, "1122334458")
        self.assertEqual(charge_points[3].cpo, self.cpo)
        self.assertEqual(charge_points[3].application, application)
        self.assertEqual(charge_points[3].station_id, "FR000012616553")
        self.assertEqual(charge_points[3].station_name, "1PACTE")
        self.assertEqual(charge_points[3].nominal_power, 22)

        self.assertEqual(charge_points[4].charge_point_id, "FR000028067822")
        self.assertEqual(charge_points[4].current_type, "AC")
        self.assertEqual(str(charge_points[4].installation_date), "2023-06-16")
        self.assertEqual(charge_points[4].mid_id, "123450-14")
        self.assertEqual(str(charge_points[4].measure_date), "2023-09-01")
        self.assertEqual(charge_points[4].measure_energy, 98765.430)
        self.assertEqual(charge_points[4].is_article_2, False)
        self.assertEqual(charge_points[4].measure_reference_point_id, "1122334459")
        self.assertEqual(charge_points[4].cpo, self.cpo)
        self.assertEqual(charge_points[4].application, application)
        self.assertEqual(charge_points[4].station_id, "FR000028067822")
        self.assertEqual(charge_points[4].station_name, "Carry-le-Rouet")
        self.assertEqual(charge_points[4].nominal_power, 36)

    def test_get_applications_ok(self):
        application = ElecChargePointApplication.objects.create(cpo=self.cpo)
        application2 = ElecChargePointApplication.objects.create(cpo=self.cpo)

        charge_point = ElecChargePoint.objects.create(
            application=application,
            cpo=self.cpo,
            charge_point_id="ABCDE",
            current_type="AC",
            installation_date=datetime.date(2023, 2, 15),
            mid_id="123-456",
            measure_date=datetime.date(2023, 6, 29),
            measure_energy=1000.1234,
            measure_reference_point_id="123456",
            station_name="Station",
            station_id="FGHIJ",
            nominal_power=150,
        )

        charge_point2 = ElecChargePoint.objects.create(
            application=application2,
            cpo=self.cpo,
            charge_point_id="ABCDE",
            current_type="AC",
            installation_date=datetime.date(2023, 2, 15),
            mid_id="123-456",
            measure_date=datetime.date(2023, 6, 29),
            measure_energy=1000.1234,
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
                    "application_date": data["data"][0]["application_date"],  # timezone annoying stuff
                    "station_count": 1,
                    "charge_point_count": 1,
                    "power_total": 150,
                },
                {
                    "id": application2.id,
                    "cpo": cpo,
                    "status": "PENDING",
                    "application_date": data["data"][1]["application_date"],
                    "station_count": 1,
                    "charge_point_count": 1,
                    "power_total": 40,
                },
            ],
        }

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data, expected)

    def test_get_charge_points_ok(self):
        application = ElecChargePointApplication.objects.create(cpo=self.cpo)
        application2 = ElecChargePointApplication.objects.create(cpo=self.cpo)

        charge_point = ElecChargePoint.objects.create(
            application=application,
            cpo=self.cpo,
            charge_point_id="ABCDE",
            current_type="AC",
            installation_date=datetime.date(2023, 2, 15),
            mid_id="123-456",
            measure_date=datetime.date(2023, 6, 29),
            measure_energy=1000.1234,
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
            charge_point_id="ABCDE",
            current_type="AC",
            installation_date=datetime.date(2023, 2, 15),
            mid_id="123-456",
            measure_date=datetime.date(2023, 6, 29),
            measure_energy=1000.1234,
            measure_reference_point_id="123456",
            station_name="Station",
            station_id="FGHIJ",
            nominal_power=40,
            cpo_name="Bob",
            cpo_siren="67890",
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
                    "nominal_power": 150,
                    "cpo_name": "Alice",
                    "cpo_siren": "12345",
                },
                {
                    "id": charge_point2.id,
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
                    "nominal_power": 40,
                    "cpo_name": "Bob",
                    "cpo_siren": "67890",
                },
            ],
        }

        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data, expected)

    def test_get_application_details_ok(self):
        application = ElecChargePointApplication.objects.create(cpo=self.cpo)
        application2 = ElecChargePointApplication.objects.create(cpo=self.cpo)

        charge_point = ElecChargePoint.objects.create(
            application=application,
            cpo=self.cpo,
            charge_point_id="ABCDE",
            current_type="AC",
            installation_date=datetime.date(2023, 2, 15),
            mid_id="123-456",
            measure_date=datetime.date(2023, 6, 29),
            measure_energy=1000.1234,
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
            charge_point_id="ABCDE",
            current_type="AC",
            installation_date=datetime.date(2023, 2, 15),
            mid_id="123-456",
            measure_date=datetime.date(2023, 6, 29),
            measure_energy=1000.1234,
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
                    "nominal_power": 150,
                    "cpo_name": "Alice",
                    "cpo_siren": "12345",
                }
            ],
        }

        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data, expected)


TDG_MOCK_OK = [
    {
        "charge_point_id": "FR000028067822",
        "cpo_name": "111442",
        "cpo_siren": "320342975",
        "current_type": "AC",
        "maybe_article_2": False,
        "latitude": 43.3292004491334,
        "longitude": 5.143766265497639,
        "nominal_power": 36.0,
        "station_id": "FR000028067822",
        "station_name": "Carry-le-Rouet",
    },
    {
        "charge_point_id": "FR000012292701",
        "cpo_name": "Hôtel Restaurant Campanile Nogent-sur-Marne",
        "cpo_siren": "349009423",
        "current_type": "AC",
        "maybe_article_2": False,
        "latitude": 48.832677935169805,
        "longitude": 2.493569567590577,
        "nominal_power": 22.0,
        "station_id": "FR000012292701",
        "station_name": "Hôtel Restaurant Campanile Nogent-sur-Marne",
    },
    {
        "charge_point_id": "FR000012616553",
        "cpo_name": "1PACTE",
        "cpo_siren": "803719277",
        "current_type": "AC",
        "maybe_article_2": False,
        "latitude": 43.476583984941,
        "longitude": 5.476711409891,
        "nominal_power": 22.0,
        "station_id": "FR000012616553",
        "station_name": "1PACTE",
    },
    {
        "charge_point_id": "FR000011062174",
        "cpo_name": "Hotel saint Alban",
        "cpo_siren": "379629447",
        "current_type": "AC",
        "maybe_article_2": False,
        "latitude": 43.41959147913006,
        "longitude": 3.407609123225763,
        "nominal_power": 22.0,
        "station_id": "FR000011062174",
        "station_name": "Hotel saint alban",
    },
    {
        "charge_point_id": "FR000012308585",
        "cpo_name": "Résidence Les Calanques",
        "cpo_siren": "812328128",
        "current_type": "AC",
        "maybe_article_2": False,
        "latitude": 41.908579309038004,
        "longitude": 8.657888301758055,
        "nominal_power": 22.0,
        "station_id": "FR000012308585",
        "station_name": "Résidence les calanques",
    },
]

TDG_MOCK_ERROR = [
    {
        "charge_point_id": "FRELCEDHDM",
        "cpo_name": "ELECTRA",
        "cpo_siren": "891624884",
        "current_type": "AC",
        "maybe_article_2": False,
        "latitude": 45.785651,
        "longitude": 4.783111,
        "nominal_power": 150.0,
        "station_id": "FRELCPECUSM",
        "station_name": "Écully - BYD & Quick",
    }
]
