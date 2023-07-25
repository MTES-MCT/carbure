# test with : python web/manage.py test admin.api.double_counting.application.tests_application.AdminDoubleCountApplicationTest.test_valid_file --keepdb
from math import prod
import os
from datetime import datetime
from admin.api.double_counting import agreements
from admin.api.double_counting.application.add import DoubleCountingAddError

from core.tests_utils import setup_current_user
from core.models import Entity, UserRights
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

from doublecount.errors import DoubleCountingError
from doublecount.models import DoubleCountingAgreement
from producers.models import ProductionSite


class Endpoint:
    change_user_role = reverse("entity-users-change-role")


User = get_user_model()


class AdminDoubleCountApplicationTest(TestCase):
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
        self.production_site.save()
        self.requested_start_year = 2023

    def add_file(self, file_name: str):
        # upload template
        carbure_home = os.environ["CARBURE_HOME"]
        filepath = f"{carbure_home}/web/fixtures/csv/test_data/{file_name}"
        fh = open(filepath, "rb")
        data = fh.read()
        fh.close()
        f = SimpleUploadedFile("dca.xlsx", data)
        response = self.client.post(
            reverse("admin-double-counting-application-add"),
            {
                "entity_id": self.admin.id,
                "producer_id": self.production_site.producer.id,
                "production_site_id": self.production_site.id,
                "file": f,
            },
        )

        return response

    def test_production_site_address_mandatory(self):
        self.production_site.address = ""
        self.production_site.save()
        response = self.add_file("dc_agreement_application_valid.xlsx")
        self.assertEqual(response.status_code, 400)

        error = response.json()["error"]
        self.assertEqual(error, DoubleCountingAddError.PRODUCTION_SITE_ADDRESS_UNDEFINED)

    def test_list_agreements(self):
        response = self.add_file("dc_agreement_application_valid.xlsx")
        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            reverse("admin-double-counting-agreements"),
            {"entity_id": self.admin.id, "year": self.requested_start_year},
        )

        data = response.json()["data"]
        pending = data["pending"]
        agreement = pending["agreements"][0]

        self.assertEqual(agreement["producer"]["id"], self.production_site.producer.id)

    def test_dc_number_generation(self):
        self.add_file("dc_agreement_application_valid.xlsx")

        agreement = DoubleCountingAgreement.objects.get(
            producer=self.production_site.producer, period_start__year=self.requested_start_year
        )

        self.assertEqual(agreement.production_site.dc_number, str(1000 + int(agreement.production_site.id)))
        self.assertEqual(agreement.agreement_id, f"FR_{agreement.production_site.dc_number}_{self.requested_start_year + 1}")
        self.assertEqual(agreement.production_site.dc_reference, agreement.agreement_id)

    def test_already_existing_agreement(self):
        self.add_file("dc_agreement_application_valid.xlsx")
        agreement = DoubleCountingAgreement.objects.get(
            producer=self.production_site.producer,
            period_start__year=self.requested_start_year,
        )
        agreement.status = DoubleCountingAgreement.PENDING
        agreement.save()

        response = self.add_file("dc_agreement_application_valid.xlsx")
        self.assertEqual(response.status_code, 400)

        error = response.json()["error"]
        self.assertEqual(error, DoubleCountingAddError.AGREEMENT_ALREADY_EXISTS)

    # TODO la fonction check_dc_file ne renvoie pas d'erreur si le fichier n'est pas valide.'
    # def test_failed_file(self):
    #     response = self.add_file("dc_agreement_application_errors_prod_integrity.xlsx")
    #     self.assertEqual(response.status_code, 400)
