# test with : python web/manage.py test doublecount.api.applications.tests_applications.DoubleCountApplicationsTest --keepdb
from math import prod
import os
from core.tests_utils import setup_current_user
from core.models import Entity, Pays, UserRights
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from doublecount.api.applications.add_application import DoubleCountingProducerAddError

from doublecount.errors import DoubleCountingError
from doublecount.factories.application import DoubleCountingApplicationFactory
from doublecount.models import DoubleCountingApplication
from producers.models import ProductionSite


class Endpoint:
    change_user_role = reverse("entity-users-change-role")


User = get_user_model()


class DoubleCountApplicationsTest(TestCase):
    fixtures = [
        "json/biofuels.json",
        "json/feedstock.json",
        "json/countries.json",
        "json/depots.json",
        "json/entities.json",
        "json/productionsites.json",
    ]

    def setUp(self):
        # self.admin = Entity.objects.filter(entity_type=Entity.ADMIN)[0]

        self.producer, _ = Entity.objects.update_or_create(name="Le Super Producteur 1", entity_type=Entity.PRODUCER)
        self.user = setup_current_user(self, "tester@carbure.local", "Tester", "gogogo", [(self.producer, "RW")], True)
        UserRights.objects.update_or_create(user=self.user, entity=self.producer, defaults={"role": UserRights.ADMIN})

        self.production_site = ProductionSite.objects.first()
        self.production_site.address = "1 rue de la Paix"
        france, _ = Pays.objects.update_or_create(code_pays="FR", name="France")
        self.production_site.country = france
        self.production_site.city = "Paris"
        self.production_site.postal_code = "75000"
        self.production_site.producer = self.producer
        self.production_site.save()
        self.requested_start_year = 2023

    def check_file(self, file_name: str):
        # upload template
        carbure_home = os.environ["CARBURE_HOME"]
        filepath = f"{carbure_home}/web/fixtures/csv/test_data/{file_name}"

        fh = open(filepath, "rb")
        data = fh.read()
        fh.close()
        f = SimpleUploadedFile("dca.xlsx", data)
        response = self.client.post(
            reverse("doublecount-applications-check-file"),
            {"entity_id": self.producer.id, "file": f},
        )
        return response

    def test_valid_file(self):
        response = self.check_file("dc_agreement_application_valid.xlsx")
        if response.status_code != 200:
            print("Failed to upload %s" % ("dc_agreement_application_valid.xlsx"))
        self.assertEqual(response.status_code, 200)

        data = response.json()["data"]
        file_data = data["file"]
        error_count = file_data["error_count"]
        self.assertEqual(error_count, 0)

        # check sourcing data
        sourcing = file_data["sourcing"]
        self.assertEqual(len(sourcing), 8)

        # check production data
        production = file_data["production"]
        self.assertEqual(len(production), 4)

    def test_has_dechets_industriels(self):
        response = self.check_file("dc_agreement_application_valid.xlsx")
        self.assertEqual(response.status_code, 200)

        data = response.json()["data"]
        file_data = data["file"]
        has_dechets_industriels = file_data["has_dechets_industriels"]
        self.assertEqual(has_dechets_industriels, True)

    def test_missing_sheet(self):
        response = self.check_file("dc_agreement_application_errors_missing_sheet.xlsx")

        data = response.json()["data"]
        file_data = data["file"]
        error_count = file_data["error_count"]
        self.assertEqual(error_count, 1)
        errors = file_data["errors"]

        error = errors["global"][0]
        self.assertEqual(error["error"], DoubleCountingError.BAD_WORKSHEET_NAME)

    def test_sourcing_row(self):
        response = self.check_file("dc_agreement_application_errors_sourcing.xlsx")

        data = response.json()["data"]
        file_data = data["file"]

        error_count = file_data["error_count"]
        self.assertEqual(error_count, 4)
        errors = file_data["errors"]

        # sourcing
        sourcing_errors = errors["sourcing_forecast"]
        self.assertEqual(len(sourcing_errors), 3)

        error1 = sourcing_errors[0]
        self.assertEqual(error1["error"], DoubleCountingError.MISSING_FEEDSTOCK)
        self.assertEqual(error1["line_number"], 8)

        error2 = sourcing_errors[1]
        self.assertEqual(error2["error"], DoubleCountingError.MISSING_COUNTRY_OF_ORIGIN)
        self.assertEqual(error2["line_number"], 12)

        error3 = sourcing_errors[2]
        self.assertEqual(error3["error"], DoubleCountingError.UNKNOWN_COUNTRY_OF_ORIGIN)
        self.assertEqual(error3["line_number"], 15)

        # global
        prod_errors = errors["production"]
        self.assertEqual(len(prod_errors), 1)

        error1 = prod_errors[0]
        self.assertEqual(error1["error"], DoubleCountingError.PRODUCTION_MISMATCH_QUOTA)
        self.assertEqual(error1["line_number"], 12)
        self.assertEqual(error1["meta"]["feedstock"], "Huile alimentaire usagée")
        self.assertEqual(error1["meta"]["estimated_production"], 10500)
        self.assertEqual(error1["meta"]["requested_quota"], 20500)

    def test_production_integrity(self):
        response = self.check_file("dc_agreement_application_errors_prod_integrity.xlsx")

        data = response.json()["data"]
        file_data = data["file"]
        error_count = file_data["error_count"]
        self.assertEqual(error_count, 4)
        errors = file_data["errors"]

        error1 = errors["production"][0]
        self.assertEqual(error1["error"], DoubleCountingError.MISSING_BIOFUEL)
        self.assertEqual(error1["line_number"], 19)

        error2 = errors["production"][1]
        self.assertEqual(error2["error"], DoubleCountingError.MISSING_BIOFUEL)
        self.assertEqual(error2["line_number"], 20)

        error3 = errors["production"][2]
        self.assertEqual(error3["error"], DoubleCountingError.MP_BC_INCOHERENT)
        self.assertEqual(error3["line_number"], 26)
        self.assertEqual(error3["meta"]["biofuel"], "EMHU")
        self.assertEqual(error3["meta"]["feedstock"], "DECHETS_INDUSTRIELS")

        error4 = errors["production"][3]
        self.assertEqual(error4["error"], DoubleCountingError.MISSING_FEEDSTOCK)
        self.assertEqual(error4["line_number"], 27)

    def test_production(self):
        response = self.check_file("dc_agreement_application_errors_production.xlsx")

        data = response.json()["data"]
        file_data = data["file"]
        error_count = file_data["error_count"]
        self.assertEqual(error_count, 2)
        errors = file_data["errors"]

        error1 = errors["production"][0]
        self.assertEqual(error1["error"], DoubleCountingError.MISSING_MAX_PRODUCTION_CAPACITY)
        self.assertEqual(error1["line_number"], 6)

        error2 = errors["production"][1]
        self.assertEqual(error2["error"], DoubleCountingError.MISSING_ESTIMATED_PRODUCTION)
        self.assertEqual(error2["line_number"], 13)

    def test_production_max(self):
        response = self.check_file("dc_agreement_application_errors_production_max.xlsx")

        data = response.json()["data"]
        file_data = data["file"]
        error_count = file_data["error_count"]
        self.assertEqual(error_count, 1)
        errors = file_data["errors"]

        error1 = errors["production"][0]
        self.assertEqual(error1["error"], DoubleCountingError.PRODUCTION_MISMATCH_PRODUCTION_MAX)
        self.assertEqual(error1["line_number"], 6)
        meta = error1["meta"]
        self.assertEqual(meta["max_production_capacity"], 5000)
        self.assertEqual(meta["estimated_production"], 8200)

    def test_global(self):
        response = self.check_file("dc_agreement_application_errors_global.xlsx")

        data = response.json()["data"]
        file_data = data["file"]
        error_count = file_data["error_count"]
        self.assertEqual(error_count, 1)
        errors = file_data["errors"]

        error1 = errors["global"][0]
        self.assertEqual(error1["error"], DoubleCountingError.PRODUCTION_MISMATCH_SOURCING)
        self.assertEqual(error1["meta"]["feedstock"], "HUILE_ALIMENTAIRE_USAGEE")
        self.assertEqual(error1["meta"]["production"], 20500)
        self.assertEqual(error1["meta"]["sourcing"], 13410)

        # error2 = errors["global"][1]
        # self.assertEqual(error2["error"], DoubleCountingError.POME_GT_2000)
        # self.assertEqual(error2["meta"]["requested_production"], 8200)

    def test_unknow_year(self):
        response = self.check_file("dc_agreement_application_errors_unknow_year.xlsx")

        data = response.json()["data"]
        file_data = data["file"]
        error_count = file_data["error_count"]
        self.assertEqual(error_count, 1)
        errors = file_data["errors"]

        error1 = errors["global"][0]
        self.assertEqual(error1["error"], DoubleCountingError.UNKNOWN_YEAR)

    def test_invalid_year_and_missing_data(self):
        response = self.check_file("dc_agreement_application_errors_invalid_year_and_missing_data.xlsx")

        data = response.json()["data"]
        file_data = data["file"]
        error_count = file_data["error_count"]
        self.assertEqual(error_count, 3)
        errors = file_data["errors"]

        error1 = errors["production"][0]
        self.assertEqual(error1["error"], DoubleCountingError.INVALID_YEAR)
        self.assertEqual(error1["line_number"], 26)

        error2 = errors["production"][1]
        self.assertEqual(error2["error"], DoubleCountingError.INVALID_YEAR)
        self.assertEqual(error2["line_number"], 27)

        error3 = errors["production"][2]
        self.assertEqual(error3["error"], DoubleCountingError.MISSING_DATA)
        self.assertEqual(error3["meta"]["tab_name"], "Production prévisionelle")

    def create_application(self):
        app = DoubleCountingApplicationFactory.create(
            producer=self.production_site.producer,
            production_site=self.production_site,
            period_start__year=self.requested_start_year,
            status=DoubleCountingApplication.PENDING,
        )
        return app

    def test_application_details(self):
        app = self.create_application()

        response = self.client.get(
            reverse("doublecount-applications-details"),
            {"entity_id": self.producer.id, "dca_id": app.id},
        )

        application = response.json()["data"]

        production_site = application["production_site"]
        self.assertEqual(production_site["id"], self.production_site.id)
        self.assertEqual(production_site["inputs"], [])
        self.assertEqual(production_site["certificates"], [])

    ######################@

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
            "entity_id": self.producer.id,
            "producer_id": self.producer.id,
            "production_site_id": self.production_site.id,
            "file": f,
        }
        if additional_data is not None:
            post_data.update(additional_data)

        response = self.client.post(reverse("doublecount-applications-add-application"), post_data)

        return response

    def test_production_site_address_mandatory(self):
        self.production_site.address = ""
        self.production_site.save()
        response = self.add_file("dc_agreement_application_valid.xlsx")
        self.assertEqual(response.status_code, 400)

        error = response.json()["error"]
        self.assertEqual(error, DoubleCountingProducerAddError.PRODUCTION_SITE_ADDRESS_UNDEFINED)

    def add_application(self):
        response = self.add_file("dc_agreement_application_valid.xlsx")
        self.assertEqual(response.status_code, 200)

        application = DoubleCountingApplication.objects.get(
            producer=self.producer, period_start__year=self.requested_start_year
        )
        created_at = application.created_at

        # 1 - status should be PENDING
        self.assertEqual(application.status, DoubleCountingApplication.PENDING)

        # 3 - test upload twice
        response = self.add_file("dc_agreement_application_valid.xlsx")
        self.assertEqual(response.status_code, 400)
        error = response.json()["error"]
        self.assertEqual(error, DoubleCountingProducerAddError.APPLICATION_ALREADY_EXISTS)

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
        self.assertEqual(error, DoubleCountingProducerAddError.APPLICATION_ALREADY_RECEIVED)
