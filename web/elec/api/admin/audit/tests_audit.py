# test with : python web/manage.py test elec.api.admin.audit.tests_audit.ElecAdminAuditTest --keepdb

import datetime
from core.tests_utils import setup_current_user
from core.models import Entity
from django.test import TestCase
from django.urls import reverse
from elec.models import ElecChargePointApplication, ElecChargePoint


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

    def test_get_years(self):
        response = self.client.get(
            reverse("elec-admin-audit-years"),
            {"entity_id": self.admin.id},
        )
        data = response.json()
        years = data["data"]
        self.assertEqual(len(years), 0)
