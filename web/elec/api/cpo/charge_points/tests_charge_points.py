import datetime
import os
from core.tests_utils import setup_current_user
from core.models import Entity
from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from elec.models.elec_charge_point import ElecChargePoint

from elec.models.elec_charge_point_application import ElecChargePointApplication


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

    def test_check_charge_point_certificate_wrong_entity(self):
        filepath = "%s/web/fixtures/csv/test_data/points-de-recharge-errors.xlsx" % (os.environ["CARBURE_HOME"])

        with open(filepath, "rb") as reader:
            file = SimpleUploadedFile("points-de-recharge-errors.xlsx", reader.read())

        response = self.client.post(
            reverse("elec-cpo-charge-points-check-application"),
            {"entity_id": self.operator.id, "file": file},
        )

        data = response.json()
        self.assertEqual(response.status_code, 403)
        self.assertEqual(data["error"], "WRONG_ENTITY_TYPE")

    def test_check_charge_point_certificate_errors(self):
        filepath = "%s/web/fixtures/csv/test_data/points-de-recharge-errors.xlsx" % (os.environ["CARBURE_HOME"])

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
                "charging_point_count": 0,
                "errors": [
                    {
                        "error": "MISSING_CHARGING_POINT_IN_DATAGOUV",
                        "meta": ["ABCDE", "FGHIJ", "KLMOPQ"],
                    }
                ],
                "error_count": 1,
            },
        }

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), expected)

    def test_check_charge_point_certificate_ok(self):
        filepath = "%s/web/fixtures/csv/test_data/points-de-recharge-ok.xlsx" % (os.environ["CARBURE_HOME"])

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
                "charging_point_count": 5,
                "errors": [],
                "error_count": 0,
            },
        }

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected)

    def test_add_charge_point_certificate_errors(self):
        filepath = "%s/web/fixtures/csv/test_data/points-de-recharge-errors.xlsx" % (os.environ["CARBURE_HOME"])

        with open(filepath, "rb") as reader:
            file = SimpleUploadedFile("points-de-recharge-errors.xlsx", reader.read())

        response = self.client.post(
            reverse("elec-cpo-charge-points-add-application"),
            {"entity_id": self.cpo.id, "file": file},
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"status": "error", "error": "VALIDATION_FAILED"})

    def test_add_charge_point_certificate_ok(self):
        filepath = "%s/web/fixtures/csv/test_data/points-de-recharge-ok.xlsx" % (os.environ["CARBURE_HOME"])

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
        self.assertEqual(charge_points[0].current_type, "CC")
        self.assertEqual(str(charge_points[0].installation_date), "2023-06-12")
        self.assertEqual(charge_points[0].lne_certificate, "123456-10")
        self.assertEqual(str(charge_points[0].meter_reading_date), "2023-08-28")
        self.assertEqual(charge_points[0].meter_reading_energy, 98765.430)
        self.assertEqual(charge_points[0].is_using_reference_meter, True)
        self.assertEqual(charge_points[0].is_auto_consumption, True)
        self.assertEqual(charge_points[0].has_article_4_regularization, True)
        self.assertEqual(charge_points[0].reference_meter_id, "1122334455")
        self.assertEqual(charge_points[0].cpo, self.cpo)
        self.assertEqual(charge_points[0].application, application)

        self.assertEqual(charge_points[1].charge_point_id, "FR000012292701")
        self.assertEqual(charge_points[1].current_type, "CA")
        self.assertEqual(str(charge_points[1].installation_date), "2023-06-13")
        self.assertEqual(charge_points[1].lne_certificate, "123457-11")
        self.assertEqual(str(charge_points[1].meter_reading_date), "2023-08-29")
        self.assertEqual(charge_points[1].meter_reading_energy, 98765.430)
        self.assertEqual(charge_points[1].is_using_reference_meter, True)
        self.assertEqual(charge_points[1].is_auto_consumption, True)
        self.assertEqual(charge_points[1].has_article_4_regularization, False)
        self.assertEqual(charge_points[1].reference_meter_id, "1122334456")
        self.assertEqual(charge_points[1].cpo, self.cpo)
        self.assertEqual(charge_points[1].application, application)

        self.assertEqual(charge_points[2].charge_point_id, "FR000012308585")
        self.assertEqual(charge_points[2].current_type, "CC")
        self.assertEqual(str(charge_points[2].installation_date), "2023-06-14")
        self.assertEqual(charge_points[2].lne_certificate, "123458-12")
        self.assertEqual(str(charge_points[2].meter_reading_date), "2023-08-30")
        self.assertEqual(charge_points[2].meter_reading_energy, 98765.430)
        self.assertEqual(charge_points[2].is_using_reference_meter, True)
        self.assertEqual(charge_points[2].is_auto_consumption, False)
        self.assertEqual(charge_points[2].has_article_4_regularization, False)
        self.assertEqual(charge_points[2].reference_meter_id, "1122334457")
        self.assertEqual(charge_points[2].cpo, self.cpo)
        self.assertEqual(charge_points[2].application, application)

        self.assertEqual(charge_points[3].charge_point_id, "FR000012616553")
        self.assertEqual(charge_points[3].current_type, "CA")
        self.assertEqual(str(charge_points[3].installation_date), "2023-06-15")
        self.assertEqual(charge_points[3].lne_certificate, "123459-13")
        self.assertEqual(str(charge_points[3].meter_reading_date), "2023-08-31")
        self.assertEqual(charge_points[3].meter_reading_energy, 98765.430)
        self.assertEqual(charge_points[3].is_using_reference_meter, False)
        self.assertEqual(charge_points[3].is_auto_consumption, False)
        self.assertEqual(charge_points[3].has_article_4_regularization, True)
        self.assertEqual(charge_points[3].reference_meter_id, "1122334458")
        self.assertEqual(charge_points[3].cpo, self.cpo)
        self.assertEqual(charge_points[3].application, application)

        self.assertEqual(charge_points[4].charge_point_id, "FR000028067822")
        self.assertEqual(charge_points[4].current_type, "CC")
        self.assertEqual(str(charge_points[4].installation_date), "2023-06-16")
        self.assertEqual(charge_points[4].lne_certificate, "123450-14")
        self.assertEqual(str(charge_points[4].meter_reading_date), "2023-09-01")
        self.assertEqual(charge_points[4].meter_reading_energy, 98765.430)
        self.assertEqual(charge_points[4].is_using_reference_meter, False)
        self.assertEqual(charge_points[4].is_auto_consumption, True)
        self.assertEqual(charge_points[4].has_article_4_regularization, False)
        self.assertEqual(charge_points[4].reference_meter_id, "1122334459")
        self.assertEqual(charge_points[4].cpo, self.cpo)
        self.assertEqual(charge_points[4].application, application)

    def test_get_applications_ok(self):
        application = ElecChargePointApplication.objects.create(cpo=self.cpo)
        application2 = ElecChargePointApplication.objects.create(cpo=self.cpo)

        charge_point = ElecChargePoint.objects.create(
            application=application,
            cpo=self.cpo,
            charge_point_id="ABCDE",
            current_type="AC",
            installation_date=datetime.date(2023, 2, 15),
            lne_certificate="123-456",
            meter_reading_date=datetime.date(2023, 6, 29),
            meter_reading_energy=1000.1234,
            reference_meter_id="123456",
            station_name="Station",
            station_id="FGHIJ",
        )

        charge_point2 = ElecChargePoint.objects.create(
            application=application2,
            cpo=self.cpo,
            charge_point_id="ABCDE",
            current_type="AC",
            installation_date=datetime.date(2023, 2, 15),
            lne_certificate="123-456",
            meter_reading_date=datetime.date(2023, 6, 29),
            meter_reading_energy=1000.1234,
            reference_meter_id="123456",
            station_name="Station",
            station_id="FGHIJ",
        )

        response = self.client.get(
            reverse("elec-cpo-charge-points-get-applications"),
            {"entity_id": self.cpo.id},
        )

        data = response.json()

        expected = {
            "status": "success",
            "data": [
                {
                    "id": application.id,
                    "cpo": self.cpo.name,
                    "status": "PENDING",
                    "application_date": data["data"][0]["application_date"],  # timezone annoying stuff
                    "station_count": 1,
                    "charging_point_count": 1,
                    "power_total": 1000.12,
                },
                {
                    "id": application2.id,
                    "cpo": self.cpo.name,
                    "status": "PENDING",
                    "application_date": data["data"][1]["application_date"],
                    "station_count": 1,
                    "charging_point_count": 1,
                    "power_total": 1000.12,
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
            lne_certificate="123-456",
            meter_reading_date=datetime.date(2023, 6, 29),
            meter_reading_energy=1000.1234,
            reference_meter_id="123456",
            station_name="Station",
            station_id="FGHIJ",
        )

        charge_point2 = ElecChargePoint.objects.create(
            application=application2,
            cpo=self.cpo,
            charge_point_id="ABCDE",
            current_type="AC",
            installation_date=datetime.date(2023, 2, 15),
            lne_certificate="123-456",
            meter_reading_date=datetime.date(2023, 6, 29),
            meter_reading_energy=1000.1234,
            reference_meter_id="123456",
            station_name="Station",
            station_id="FGHIJ",
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
                    "lne_certificate": "123-456",
                    "meter_reading_date": "2023-06-29",
                    "meter_reading_energy": 1000.12,
                    "is_using_reference_meter": False,
                    "is_auto_consumption": False,
                    "has_article_4_regularization": False,
                    "reference_meter_id": "123456",
                    "station_name": "Station",
                    "station_id": "FGHIJ",
                },
                {
                    "id": charge_point2.id,
                    "cpo": self.cpo.name,
                    "charge_point_id": "ABCDE",
                    "current_type": "AC",
                    "installation_date": "2023-02-15",
                    "lne_certificate": "123-456",
                    "meter_reading_date": "2023-06-29",
                    "meter_reading_energy": 1000.12,
                    "is_using_reference_meter": False,
                    "is_auto_consumption": False,
                    "has_article_4_regularization": False,
                    "reference_meter_id": "123456",
                    "station_name": "Station",
                    "station_id": "FGHIJ",
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
            lne_certificate="123-456",
            meter_reading_date=datetime.date(2023, 6, 29),
            meter_reading_energy=1000.1234,
            reference_meter_id="123456",
            station_name="Station",
            station_id="FGHIJ",
        )

        charge_point2 = ElecChargePoint.objects.create(
            application=application2,
            cpo=self.cpo,
            charge_point_id="ABCDE",
            current_type="AC",
            installation_date=datetime.date(2023, 2, 15),
            lne_certificate="123-456",
            meter_reading_date=datetime.date(2023, 6, 29),
            meter_reading_energy=1000.1234,
            reference_meter_id="123456",
            station_name="Station",
            station_id="FGHIJ",
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
                    "lne_certificate": "123-456",
                    "meter_reading_date": "2023-06-29",
                    "meter_reading_energy": 1000.12,
                    "is_using_reference_meter": False,
                    "is_auto_consumption": False,
                    "has_article_4_regularization": False,
                    "reference_meter_id": "123456",
                    "station_name": "Station",
                    "station_id": "FGHIJ",
                }
            ],
        }

        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data, expected)
