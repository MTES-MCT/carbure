# Test : python web/manage.py test elec.api.cpo.meters.test_meters

import datetime

from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from core.models import Entity
from core.tests_utils import setup_current_user
from elec.models import ElecChargePoint, ElecChargePointApplication, ElecMeter, ElecMeterReading, ElecMeterReadingApplication


class ElecMeterTest(TestCase):
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

        application = ElecChargePointApplication.objects.create(cpo=self.cpo)
        application.created_at = datetime.date(2023, 12, 28)
        application.save()

        self.reading_application = ElecMeterReadingApplication.objects.create(
            cpo=self.cpo,
            quarter=3,
            year=2023,
        )

        self.charge_point = ElecChargePoint.objects.create(
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

        self.meter1 = ElecMeter.objects.create(
            charge_point=self.charge_point,
            initial_index=1000,
            initial_index_date=datetime.date(2023, 2, 15),
            mid_certificate="MID_ABCD",
        )

        self.meter2 = ElecMeter.objects.create(
            charge_point=self.charge_point,
            initial_index=700,
            initial_index_date=datetime.date(2023, 10, 20),
            mid_certificate="MID_EFGH",
        )

        self.charge_point.current_meter = self.meter2
        self.charge_point.save()

        self.meter_reading = ElecMeterReading.objects.create(
            extracted_energy=1000,
            renewable_energy=1000,
            reading_date=datetime.date(2023, 11, 15),
            cpo=self.cpo,
            application=self.reading_application,
            meter=self.meter2,
        )

    def test_add_elec_meter_success(self):
        url = reverse("elec-cpo-meters-add-meter")
        data = {
            "charge_point": self.charge_point.id,
            "initial_index": 1000,
            "initial_index_date": datetime.date(2023, 12, 15),
            "mid_certificate": "MID_ABCD",
            "entity_id": self.cpo.id,
        }
        response = self.client.post(url, data)
        assert response.status_code == status.HTTP_200_OK

    def test_add_elec_meter_invalid_params(self):
        url = reverse("elec-cpo-meters-add-meter")
        data = {
            "charge_point": 999999999,
            "initial_index": 1000,
            "initial_index_date": datetime.date(2023, 2, 15),
            "mid_certificate": "MID_ABCD",
            "entity_id": self.cpo.id,
        }
        response = self.client.post(url, data)
        data = response.json()
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert data["error"] == "MALFORMED_PARAMS"

    def test_add_elec_meter_cp_not_found_on_cpo(self):
        url = reverse("elec-cpo-meters-add-meter")
        data = {
            "charge_point": self.charge_point.id,
            "initial_index": 1000,
            "initial_index_date": datetime.date(2023, 2, 15),
            "mid_certificate": "MID_ABCD",
            "entity_id": self.cpo.id,
        }
        cpo2 = Entity.objects.create(
            name="CPO2",
            entity_type=Entity.CPO,
            has_elec=True,
        )
        self.charge_point.cpo = cpo2
        self.charge_point.save()
        response = self.client.post(url, data)
        data = response.json()
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert data["error"] == "CP_NOT_FOUND_ON_CPO"

    def test_add_elec_meter_initial_date_nok(self):
        url = reverse("elec-cpo-meters-add-meter")
        data = {
            "charge_point": self.charge_point.id,
            "initial_index": 1000,
            "initial_index_date": datetime.date(2023, 10, 15),
            "mid_certificate": "MID_ABCD",
            "entity_id": self.cpo.id,
        }
        response = self.client.post(url, data)
        data = response.json()
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert data["error"] == "NEW_INITIAL_INDEX_DATE_KO"

    def test_get_elec_meters_success(self):
        url = reverse("elec-cpo-meters-get-meters")
        data = {
            "charge_point_id": self.charge_point.id,
            "entity_id": self.cpo.id,
        }

        response = self.client.get(url, data)
        data = response.json()

        expected = {
            "status": "success",
            "data": [
                {
                    "id": self.meter1.id,
                    "mid_certificate": "MID_ABCD",
                    "initial_index": 1000,
                    "initial_index_date": "2023-02-15",
                    "charge_point": self.charge_point.id,
                },
                {
                    "id": self.meter2.id,
                    "mid_certificate": "MID_EFGH",
                    "initial_index": 700,
                    "initial_index_date": "2023-10-20",
                    "charge_point": self.charge_point.id,
                },
            ],
        }
        assert response.status_code == status.HTTP_200_OK
        assert data == expected

    def test_get_elec_meters_invalid_params(self):
        url = reverse("elec-cpo-meters-get-meters")
        data = {
            "charge_point_id": 999999999,
            "entity_id": self.cpo.id,
        }
        response = self.client.get(url, data)
        data = response.json()
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert data["error"] == "MALFORMED_PARAMS"

    def test_get_elec_meters_cp_not_found_on_cpo(self):
        url = reverse("elec-cpo-meters-get-meters")
        data = {
            "charge_point_id": self.charge_point.id,
            "entity_id": self.cpo.id,
        }
        cpo2 = Entity.objects.create(
            name="CPO2",
            entity_type=Entity.CPO,
            has_elec=True,
        )
        self.charge_point.cpo = cpo2
        self.charge_point.save()
        response = self.client.get(url, data)
        data = response.json()
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert data["error"] == "CP_NOT_FOUND_ON_CPO"
