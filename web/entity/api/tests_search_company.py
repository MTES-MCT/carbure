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
            {"registration_id": "542051180"},
        )
        data = response.json()
        company_preview = data["data"]["company_preview"]
        self.assertEqual(company_preview["legal_name"], "TOTALENERGIES SE")
        print("company_preview: ", company_preview)

    def test_search_company_already_exists(self):
        siren = "542051180"
        Entity.objects.create(name="name", registration_id=siren)

        response = self.client.post(
            reverse("entity-search-company"),
            {"registration_id": siren},
        )
        data = response.json()
        warning = data["data"]["warning"]
        print("warning: ", warning)
        self.assertEqual(warning["code"], "REGISTRATION_ID_ALREADY_USED")

    def test_search_unexisting_company(self):
        response = self.client.post(
            reverse("entity-search-company"),
            {"registration_id": "753991464"},
        )
        data = response.json()
        error_code = data["error"]
        self.assertEqual(error_code, "NO_COMPANY_FOUND")
