# test with : python web/manage.py test elec.api.admin.audit.tests_audit.ElecAdminAuditTest --keepdb

import datetime
import stat
from core.tests_utils import setup_current_user
from core.models import Entity
from django.test import TestCase
from django.urls import reverse

from elec.models.elec_charge_point import ElecChargePoint
from elec.models.elec_charge_point_application import ElecChargePointApplication


class ElecAdminAuditTest(TestCase):
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

    def create_application(self):
        application = ElecChargePointApplication.objects.create(cpo=self.cpo)
        application2 = ElecChargePointApplication.objects.create(cpo=self.cpo, status=ElecChargePointApplication.ACCEPTED)

        ElecChargePoint.objects.create(
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
            cpo_name="",
            cpo_siren="",
        )

        ElecChargePoint.objects.create(
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
            cpo_name="",
            cpo_siren="",
        )

    def test_get_years(self):
        # no year
        response = self.client.get(
            reverse("elec-admin-audit-years"),
            {"entity_id": self.admin.id},
        )
        data = response.json()
        years = data["data"]
        self.assertEqual(len(years), 0)

        # 1 year
        self.create_application()
        response = self.client.get(
            reverse("elec-admin-audit-years"),
            {"entity_id": self.admin.id},
        )
        data = response.json()
        years = data["data"]
        self.assertEqual(len(years), 1)

    def test_get_snapshot(self):
        # no snapshot
        response = self.client.get(
            reverse("elec-admin-audit-snapshot"),
            {"entity_id": self.admin.id, "year": 2024},
        )
        data = response.json()
        snapshot = data["data"]
        self.assertEqual(snapshot["charge_points_applications"], 0)

        # filled snapshot
        self.create_application()
        response = self.client.get(
            reverse("elec-admin-audit-snapshot"),
            {"entity_id": self.admin.id, "year": 2024},
        )
        data = response.json()
        snapshot = data["data"]
        self.assertEqual(snapshot["charge_points_applications"], 2)
        self.assertEqual(snapshot["charge_points_applications_pending"], 1)
        self.assertEqual(snapshot["charge_points_applications_history"], 1)
