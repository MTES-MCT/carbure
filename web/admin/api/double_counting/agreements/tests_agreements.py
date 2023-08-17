# test with : python web/manage.py test admin.api.double_counting.tests_double_counting.AdminDoubleCountTest --keepdb
from datetime import date
import json
from nis import cat
from operator import le
import os
import stat
from admin.api.double_counting.applications.add import DoubleCountingAddError
from admin.api.double_counting.applications.approve_application import DoubleCountingApplicationApproveError
from certificates.models import DoubleCountingRegistration

from core.tests_utils import setup_current_user
from core.models import Entity, MatierePremiere, Pays, UserRights
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from doublecount.factories import (
    DoubleCountingApplicationFactory,
    DoubleCountingProductionFactory,
    DoubleCountingSourcingFactory,
    production,
)
from doublecount.factories import agreement
from doublecount.factories.agreement import DoubleCountingRegistrationFactory

from doublecount.models import DoubleCountingApplication, DoubleCountingDocFile, DoubleCountingProduction
from producers.models import ProductionSite


class Endpoint:
    change_user_role = reverse("entity-users-change-role")


User = get_user_model()


class AdminDoubleCountAgreementsTest(TestCase):
    fixtures = [
        "json/biofuels.json",
        "json/feedstock.json",
        "json/countries.json",
        "json/depots.json",
        "json/entities.json",
        "json/productionsites.json",
    ]

    def setUp(self):
        self.admin = Entity.objects.filter(entity_type=Entity.ADMIN)[0]

        self.user = setup_current_user(self, "tester@carbure.local", "Tester", "gogogo", [(self.admin, "RW")], True)

        self.producer, _ = Entity.objects.update_or_create(name="Le Super Producteur 1", entity_type="Producteur")
        UserRights.objects.update_or_create(user=self.user, entity=self.producer, defaults={"role": UserRights.ADMIN})

        self.production_site = ProductionSite.objects.first()
        self.production_site.address = "1 rue de la Paix"
        france, _ = Pays.objects.update_or_create(code_pays="FR", name="France")
        self.production_site.country = france
        self.production_site.city = "Paris"
        self.production_site.postal_code = "75000"
        self.production_site.save()
        self.requested_start_year = 2023

    def create_agreement(self):
        agreement = DoubleCountingRegistrationFactory.create(
            production_site=self.production_site, valid_from=date(self.requested_start_year, 1, 1)
        )
        return agreement

    def test_get_agreements(self):
        agreement1 = self.create_agreement()
        self.create_agreement()

        response = self.client.get(reverse("admin-double-counting-agreements"), {"entity_id": self.admin.id})
        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        active_agreements = data["active"]
        self.assertEqual(active_agreements[0]["certificate_id"], agreement1.certificate_id)
        self.assertEqual(len(active_agreements), 2)

    def test_export_agreements(self):
        self.create_agreement()

        # test that the response is an excel file
        response = self.client.get(
            reverse("admin-double-counting-agreements"), {"entity_id": self.admin.id, "as_excel_file": "true"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
