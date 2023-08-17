# test with : python web/manage.py test admin.api.double_counting.tests_double_counting.AdminDoubleCountTest --keepdb
from datetime import date
import json
from nis import cat
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

from doublecount.models import DoubleCountingApplication, DoubleCountingDocFile, DoubleCountingProduction
from producers.models import ProductionSite


class Endpoint:
    change_user_role = reverse("entity-users-change-role")


User = get_user_model()


class AdminDoubleCountApplicationsTest(TestCase):
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

    def add_file(self, file_name: str, additional_data=None):
        # upload template
        carbure_home = os.environ["CARBURE_HOME"]
        filepath = f"{carbure_home}/web/fixtures/csv/test_data/{file_name}"
        fh = open(filepath, "rb")
        data = fh.read()
        fh.close()
        f = SimpleUploadedFile("dca.xlsx", data)

        # Add data properties to the post data if provided
        post_data = {
            "entity_id": self.admin.id,
            "producer_id": self.production_site.producer.id,
            "production_site_id": self.production_site.id,
            "file": f,
        }
        if additional_data is not None:
            post_data.update(additional_data)

        response = self.client.post(reverse("admin-double-counting-application-add"), post_data)

        return response

    def create_application(self):
        app = DoubleCountingApplicationFactory.create(
            producer=self.production_site.producer,
            production_site=self.production_site,
            period_start__year=self.requested_start_year,
            status=DoubleCountingApplication.PENDING,
        )

        sourcing1 = DoubleCountingSourcingFactory.create(dca=app, year=self.requested_start_year)
        sourcing2 = DoubleCountingSourcingFactory.create(dca=app, year=self.requested_start_year)
        production1 = DoubleCountingProductionFactory.create(
            dca=app, feedstock=sourcing2.feedstock, year=self.requested_start_year + 1, approved_quota=-1
        )
        production2 = DoubleCountingProductionFactory.create(
            dca=app, feedstock=sourcing2.feedstock, year=self.requested_start_year + 1, approved_quota=-1
        )

        return app, sourcing1, production1, sourcing1, production2

    def test_add_application(self):
        # 1 - test add file
        response = self.add_file("dc_agreement_application_valid.xlsx")
        self.assertEqual(response.status_code, 200)
        application = DoubleCountingApplication.objects.get(
            producer=self.production_site.producer, period_start__year=self.requested_start_year
        )
        created_at = application.created_at

        # 1.1 - status should be PENDING
        self.assertEqual(application.status, DoubleCountingApplication.PENDING)

        # 1.2 - test production requested
        productions = DoubleCountingProduction.objects.filter(dca_id=application.id, year=2023)
        self.assertEqual(productions[0].requested_quota, 20500)
        self.assertEqual(productions[1].requested_quota, 8200)

        # 1.3  test_dc_number_generation
        self.assertEqual(application.production_site.dc_number, str(1000 + int(application.production_site.id)))
        self.assertEqual(application.agreement_id, f"FR_{application.production_site.dc_number}_{self.requested_start_year}")
        self.assertEqual(application.production_site.dc_reference, application.agreement_id)

        # 1.2 - check period_start and period_end
        self.assertEqual(application.period_start, date(self.requested_start_year, 1, 1))
        self.assertEqual(application.period_end, date(self.requested_start_year + 1, 12, 31))

        # 2 - test if file uploaded
        docFile = DoubleCountingDocFile.objects.filter(agreement_id=application.agreement_id).first()
        self.assertEqual(docFile.file_name, "dca.xlsx")
        self.assertEqual(docFile.agreement_id, application.agreement_id)

        # 3 - test upload twice
        response = self.add_file("dc_agreement_application_valid.xlsx")
        self.assertEqual(response.status_code, 400)
        error = response.json()["error"]
        self.assertEqual(error, DoubleCountingAddError.APPLICATION_ALREADY_EXISTS)

        # 4 - test should replace
        response = self.add_file("dc_agreement_application_valid.xlsx", {"should_replace": "true"})
        self.assertEqual(response.status_code, 200)
        application = DoubleCountingApplication.objects.get(
            producer=self.production_site.producer, period_start__year=self.requested_start_year
        )
        self.assertNotEqual(application.created_at, created_at)

        # 5 - cannot be replaced if already accepted
        application.status = DoubleCountingApplication.ACCEPTED
        application.save()
        response = self.add_file("dc_agreement_application_valid.xlsx", {"should_replace": "true"})
        self.assertEqual(response.status_code, 400)
        error = response.json()["error"]
        self.assertEqual(error, DoubleCountingAddError.APPLICATION_ALREADY_RECEIVED)

    def test_production_site_address_mandatory(self):
        self.production_site.address = ""
        self.production_site.save()
        response = self.add_file("dc_agreement_application_valid.xlsx")
        self.assertEqual(response.status_code, 400)

        error = response.json()["error"]
        self.assertEqual(error, DoubleCountingAddError.PRODUCTION_SITE_ADDRESS_UNDEFINED)

    def test_list_applications(self):
        self.create_application()

        response = self.client.get(
            reverse("admin-double-counting-applications"),
            {"entity_id": self.admin.id, "year": self.requested_start_year},
        )

        data = response.json()["data"]
        pending = data["pending"]
        application = pending[0]

        self.assertEqual(application["producer"]["id"], self.production_site.producer.id)

    def test_application_details(self):
        app, sourcing, production, _, _ = self.create_application()

        response = self.client.get(
            reverse("admin-double-counting-application-details"),
            {"entity_id": self.admin.id, "dca_id": app.id},
        )

        application = response.json()["data"]

        self.assertEqual(application["sourcing"][0]["id"], sourcing.id)
        self.assertEqual(application["production"][0]["id"], production.id)

        production_site = application["production_site"]
        self.assertEqual(production_site["id"], self.production_site.id)
        self.assertEqual(production_site["inputs"], [])
        self.assertEqual(production_site["certificates"], [])

    def test_approve_application(self):
        application, sourcing1, production1, sourcing2, production2 = self.create_application()

        # test approve without quotas
        params = {"dca_id": application.id, "entity_id": self.admin.id}
        response = self.client.post(reverse("admin-double-counting-application-approve"), params)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"], DoubleCountingApplicationApproveError.QUOTAS_NOT_APPROVED)
        self.assertEqual(application.status, DoubleCountingApplication.PENDING)

        # update quotas
        updated_quotas = [[production1.id, 20500], [production2.id, 8200]]
        response = self.client.post(
            reverse("admin-double-counting-application-update-approved-quotas"),
            {"entity_id": self.admin.id, "approved_quotas": json.dumps(updated_quotas), "dca_id": application.id},
        )
        self.assertEqual(response.status_code, 200)

        productions = DoubleCountingProduction.objects.filter(dca_id=application.id)
        self.assertEqual(productions[0].approved_quota, 20500)
        self.assertEqual(productions[1].approved_quota, 8200)

        application = DoubleCountingApplication.objects.get(
            producer=self.production_site.producer, period_start__year=self.requested_start_year
        )

        # test approve with quotas
        response = self.client.post(reverse("admin-double-counting-application-approve"), params)
        self.assertEqual(response.status_code, 200)
        application = DoubleCountingApplication.objects.get(
            producer=self.production_site.producer, period_start__year=self.requested_start_year
        )
        self.assertEqual(application.status, DoubleCountingApplication.ACCEPTED)

        # test agreement generation
        agreement = DoubleCountingRegistration.objects.get(certificate_id=application.agreement_id)
        self.assertEqual(agreement.valid_from, date(2023, 1, 1))
        self.assertEqual(agreement.valid_until, date(2024, 12, 31))
        self.assertEqual(agreement.production_site, application.production_site)
        self.assertEqual(agreement.certificate_id, application.agreement_id)
        self.assertEqual(agreement.application.id, application.id)
