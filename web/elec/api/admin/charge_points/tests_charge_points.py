import datetime

from django.test import TestCase
from django.urls import reverse

from core.models import Entity
from core.tests_utils import setup_current_user
from elec.models import ElecChargePoint, ElecChargePointApplication, ElecMeter


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

        meter_data = {
            "mid_certificate": "123-456",
            "initial_index": 1000.123,
            "initial_index_date": datetime.date(2023, 6, 29),
            "charge_point": None,
        }

        self.meter = ElecMeter.objects.create(**meter_data)
        self.meter2 = ElecMeter.objects.create(**meter_data)

    def test_get_applications_wrong_entity(self):
        response = self.client.get(
            reverse("elec-admin-charge-points-get-applications"),
            {"entity_id": self.cpo.id, "company_id": self.cpo.id},
        )

        data = response.json()
        assert response.status_code == 404
        assert data["error"] == "ENTITY_NOT_FOUND"

    def test_get_applications_ok(self):
        application = ElecChargePointApplication.objects.create(cpo=self.cpo)
        application.created_at = datetime.date(2023, 12, 28)
        application.save()

        application2 = ElecChargePointApplication.objects.create(cpo=self.cpo)
        application2.created_at = datetime.date(2023, 12, 29)
        application2.save()

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
            cpo_name="",
            cpo_siren="",
        )

        ElecChargePoint.objects.create(
            application=application2,
            cpo=self.cpo,
            charge_point_id="ABCDE",
            current_type="AC",
            installation_date=datetime.date(2023, 2, 15),
            current_meter=self.meter2,
            measure_reference_point_id="123456",
            station_name="Station",
            station_id="FGHIJ",
            nominal_power=40,
            cpo_name="",
            cpo_siren="",
        )

        response = self.client.get(
            reverse("elec-admin-charge-points-get-applications"),
            {"entity_id": self.admin.id, "company_id": self.cpo.id},
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
            ],
        }

        assert response.status_code == 200
        assert data == expected

    def test_get_charge_points_ok(self):
        application = ElecChargePointApplication.objects.create(cpo=self.cpo)
        application.created_at = datetime.date(2023, 12, 28)
        application.save()
        application2 = ElecChargePointApplication.objects.create(cpo=self.cpo)
        application2.created_at = datetime.date(2023, 12, 28)
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

        self.meter.charge_point = charge_point
        self.meter.save()

        charge_point2 = ElecChargePoint.objects.create(
            application=application2,
            cpo=self.cpo,
            charge_point_id="ABCDE",
            current_type="AC",
            installation_date=datetime.date(2023, 2, 15),
            current_meter=self.meter2,
            measure_reference_point_id="123456",
            station_name="Station",
            station_id="FGHIJ",
            nominal_power=40,
            cpo_name="Bob",
            cpo_siren="67890",
        )

        self.meter2.charge_point = charge_point2
        self.meter2.save()

        response = self.client.get(
            reverse("elec-admin-charge-points-get-charge-points"),
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
                    "application_date": "2023-12-28",
                    "installation_date": "2023-02-15",
                    "mid_id": "123-456",
                    "measure_date": "2023-06-29",
                    "measure_energy": 1000.123,
                    "latest_extracted_energy": 0,
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
                    "charge_point_id": "ABCDE",
                    "current_type": "AC",
                    "application_date": "2023-12-28",
                    "installation_date": "2023-02-15",
                    "mid_id": "123-456",
                    "measure_date": "2023-06-29",
                    "measure_energy": 1000.123,
                    "latest_extracted_energy": 0,
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

    def test_get_application_details_ok(self):
        application = ElecChargePointApplication.objects.create(cpo=self.cpo)
        application.created_at = datetime.date(2023, 12, 28)
        application.save()

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

        self.meter.charge_point = charge_point
        self.meter.save()

        response = self.client.get(
            reverse("elec-admin-charge-points-get-application-details"),
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
                    "application_date": "2023-12-28",
                    "installation_date": "2023-02-15",
                    "mid_id": "123-456",
                    "measure_date": "2023-06-29",
                    "measure_energy": 1000.123,
                    "latest_extracted_energy": 0,
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
