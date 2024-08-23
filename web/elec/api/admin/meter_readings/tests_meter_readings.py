import datetime
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from core.models import Entity
from core.tests_utils import setup_current_user
from elec.models.elec_charge_point import ElecChargePoint
from elec.models.elec_charge_point_application import ElecChargePointApplication
from elec.models.elec_meter_reading import ElecMeterReading
from elec.models.elec_meter_reading_application import ElecMeterReadingApplication
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
        "previous_reading": 600,
        "current_reading": 700,
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
        self.admin = Entity.objects.create(
            name="ADMIN",
            entity_type=Entity.ADMIN,
        )

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
            [(self.admin, "RW"), (self.cpo, "RW"), (self.operator, "RW")],
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
            extracted_energy=600,
            renewable_energy=24.92,
            reading_date=datetime.date(2024, 5, 21),
            charge_point=self.charge_point_2,
            cpo=self.cpo,
            application=self.meter_reading_application,
        )

    def test_get_applications(self):
        response = self.client.get(
            reverse("admin-elec-meter-readings-get-applications"),
            {"entity_id": self.admin.id, "company_id": self.cpo.id},
        )

        application = ElecMeterReadingApplication.objects.last()

        application_date = application.created_at.isoformat()

        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            data,
            {
                "status": "success",
                "data": [
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
            },
        )

    def test_get_application_details(self):
        response = self.client.get(
            reverse("admin-elec-meter-readings-get-application-details"),
            {"entity_id": self.admin.id, "company_id": self.cpo.id, "application_id": self.meter_reading_application.id},
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
                        "previous_reading": 500.0,
                        "current_reading": 600.0,
                        "reading_date": "2024-05-21",
                    },
                ],
            },
        )
