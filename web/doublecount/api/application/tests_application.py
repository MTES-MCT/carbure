# test with : python web/manage.py test doublecount.api.application.tests_application --keepdb
import os
from core.tests_utils import setup_current_user
from core.models import Entity, UserRights
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

from doublecount.errors import DoubleCountingError


class Endpoint:
    change_user_role = reverse("entity-users-change-role")


User = get_user_model()


class DoubleCountApplicationTest(TestCase):
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

    def check_file(self, file_name: str):
        # upload template
        carbure_home = os.environ["CARBURE_HOME"]
        filepath = f"{carbure_home}/web/fixtures/csv/test_data/{file_name}"

        fh = open(filepath, "rb")
        data = fh.read()
        fh.close()
        f = SimpleUploadedFile("dca.xlsx", data)
        response = self.client.post(
            reverse("doublecount-application-check-file"),
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

    def test_missing_sheet(self):
        response = self.check_file("dc_agreement_application_errors_missing_sheet.xlsx")

        data = response.json()["data"]
        file_data = data["file"]
        error_count = file_data["error_count"]
        self.assertEqual(error_count, 1)
        errors = file_data["errors"]

        error = errors["global"][0]
        self.assertEqual(error["error"], DoubleCountingError.BAD_WORKSHEET_NAME)
