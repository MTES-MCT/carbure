# test with : python web/manage.py test entity.api.tests_search_company.EntitySearchCompanyTest --keepdb

import datetime
import stat
from core.tests_utils import setup_current_user
from core.models import Entity
from django.test import TestCase
from django.urls import reverse

from elec.models.elec_charge_point import ElecChargePoint
from elec.models.elec_charge_point_application import ElecChargePointApplication


class EntitySearchCompanyTest(TestCase):
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
        )

    def test_search_company(self):
        response = self.client.post(
            reverse("entity-search-company"),
            {"registration_id": "753061464"},
        )
        data = response.json()
        print("data: ", data)
