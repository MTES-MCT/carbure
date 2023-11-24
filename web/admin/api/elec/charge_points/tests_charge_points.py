import datetime
from core.tests_utils import setup_current_user
from core.models import Entity
from django.test import TestCase
from django.urls import reverse
from elec.models import ElecChargePointApplication, ElecChargePoint


class ElecCharginPointsTest(TestCase):
    def setUp(self):
        self.admin = Entity.objects.create(
            name="Admin",
            entity_type=Entity.ADMIN,
            has_elec=True,
        )

        self.cpo = Entity.objects.create(
            name="CPO",
            entity_type=Entity.CPO,
            has_elec=True,
        )

        self.user = setup_current_user(
            self,
            "tester@carbure.local",
            "Tester",
            "gogogo",
            [(self.cpo, "RW"), (self.admin, "ADMIN")],
        )

    def test_get_applications_wrong_entity(self):
        response = self.client.get(
            reverse("admin-elec-charge-points-get-applications"),
            {"entity_id": self.cpo.id, "company_id": self.cpo.id},
        )

        data = response.json()
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data["error"], "ENTITY_NOT_FOUND")

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
            reverse("admin-elec-charge-points-get-applications"),
            {"entity_id": self.admin.id, "company_id": self.cpo.id},
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
            reverse("admin-elec-charge-points-get-charge-points"),
            {"entity_id": self.admin.id, "company_id": self.cpo.id},
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
            reverse("admin-elec-charge-points-get-application-details"),
            {"entity_id": self.admin.id, "company_id": self.cpo.id, "application_id": application.id},
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

    def test_accept_charge_point_certificate_ok(self):
        application = ElecChargePointApplication.objects.create(cpo=self.cpo)

        self.assertEqual(application.status, ElecChargePointApplication.PENDING)

        response = self.client.post(
            reverse("admin-elec-charge-points-accept-application"),
            {"entity_id": self.admin.id, "company_id": self.cpo.id, "application_id": application.id},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "success"})

        application.refresh_from_db()
        self.assertEqual(application.status, ElecChargePointApplication.ACCEPTED)

    def test_reject_charge_point_certificate_ok(self):
        application = ElecChargePointApplication.objects.create(cpo=self.cpo)

        self.assertEqual(application.status, ElecChargePointApplication.PENDING)

        response = self.client.post(
            reverse("admin-elec-charge-points-reject-application"),
            {"entity_id": self.admin.id, "company_id": self.cpo.id, "application_id": application.id},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "success"})

        application.refresh_from_db()
        self.assertEqual(application.status, ElecChargePointApplication.REJECTED)
