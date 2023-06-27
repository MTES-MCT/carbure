# test with : python web/manage.py test doublecount.api.application.tests_application --keepdb
import os
from core.tests_utils import setup_current_user
from core.models import Entity, UserRights
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile


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

    def test_valid_file(self):
        # upload template
        filepath = "%s/web/fixtures/csv/test_data/dc_agreement_application.xlsx" % (os.environ["CARBURE_HOME"])
        fh = open(filepath, "rb")
        data = fh.read()
        fh.close()
        f = SimpleUploadedFile("dca.xlsx", data)
        response = self.client.post(
            reverse("doublecount-application-check-file"),
            {"entity_id": self.producer.id, "file": f},
        )
        if response.status_code != 200:
            print("Failed to upload %s" % (filepath))
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
