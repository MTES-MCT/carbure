import datetime
import os

from django.test import TransactionTestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from core.models import Entity, Pays, Depot, UserRights
from producers.models import ProductionSite
from doublecount.models import (
    DoubleCountingApplication,
    DoubleCountingDocFile,
    DoubleCountingSourcing,
    DoubleCountingProduction,
)
from django_otp.plugins.otp_email.models import EmailDevice
from django.core.files.uploadedfile import SimpleUploadedFile


class DCAAPITest(TransactionTestCase):
    home = os.environ["CARBURE_HOME"]
    fixtures = [
        "{home}/web/fixtures/json/countries.json".format(home=home),
        "{home}/web/fixtures/json/feedstock.json".format(home=home),
        "{home}/web/fixtures/json/biofuels.json".format(home=home),
        "{home}/web/fixtures/json/depots.json".format(home=home),
    ]

    def setUp(self):
        user_model = get_user_model()
        self.user_email = "testuser1@toto.com"
        self.user_password = "totopouet"
        self.user1 = user_model.objects.create_user(
            email=self.user_email, name="Le Super Testeur 1", password=self.user_password
        )
        self.producer, _ = Entity.objects.update_or_create(name="Le Super Producteur 1", entity_type="Producteur")
        UserRights.objects.update_or_create(user=self.user1, entity=self.producer, role="RW")
        france = Pays.objects.get(code_pays="FR")
        today = datetime.date.today()
        d = {
            "country": france,
            "date_mise_en_service": today,
            "site_id": "SIRET XXX",
            "city": "paris",
            "postal_code": "75001",
            "manager_name": "Guillaume Caillou",
            "manager_phone": "0145247000",
            "manager_email": "test@test.net",
        }
        self.production_site, _ = ProductionSite.objects.update_or_create(producer=self.producer, name="PSITE1", defaults=d)
        Depot.objects.update_or_create(name="Depot Test", depot_id="001", country=france)

        loggedin = self.client.login(username=self.user_email, password=self.user_password)
        self.assertTrue(loggedin)
        # pass otp verification
        response = self.client.post(reverse("auth-request-otp"))
        self.assertEqual(response.status_code, 200)
        device, created = EmailDevice.objects.get_or_create(user=self.user1)
        response = self.client.post(reverse("auth-verify-otp"), {"otp_token": device.token})
        self.assertEqual(response.status_code, 200)

    def test_dca_sourcing(self):
        # download template sourcing
        response = self.client.get(reverse("api-v3-doublecount-get-template"))
        self.assertEqual(response.status_code, 200)
        # upload template
        filepath = "%s/web/fixtures/csv/test_data/dca.xlsx" % (os.environ["CARBURE_HOME"])
        fh = open(filepath, "rb")
        data = fh.read()
        fh.close()
        f = SimpleUploadedFile("dca.xlsx", data)
        response = self.client.post(
            reverse("api-v3-doublecount-upload-file"),
            {"entity_id": self.producer.id, "production_site_id": self.production_site.id, "file": f},
        )
        if response.status_code != 200:
            print("Failed to upload %s" % (filepath))
        self.assertEqual(response.status_code, 200)
        # check if it matches expectations
        dca = DoubleCountingApplication.objects.get(producer=self.producer, production_site=self.production_site)
        self.assertEqual(8, DoubleCountingSourcing.objects.filter(dca=dca).count())
        self.assertEqual(4, DoubleCountingProduction.objects.filter(dca=dca).count())

    def test_dca_upload_document(self):
        dca, created = DoubleCountingApplication.objects.get_or_create(
            producer=self.producer,
            production_site=self.production_site,
            period_start=datetime.date(2022, 1, 1),
            period_end=datetime.date(2023, 12, 31),
        )
        filepath = "%s/web/fixtures/csv/test_data/dca.xlsx" % (os.environ["CARBURE_HOME"])
        fh = open(filepath, "rb")
        data = fh.read()
        fh.close()
        f = SimpleUploadedFile("dca.xlsx", data)
        response = self.client.post(
            reverse("api-v3-doublecount-upload-doc"), {"entity_id": self.producer.id, "dca_id": dca.id, "file": f}
        )
        if response.status_code != 200:
            print("Failed to upload %s" % (filepath))
        self.assertEqual(response.status_code, 200)
        files = DoubleCountingDocFile.objects.filter(dca=dca)
        self.assertEqual(files.count(), 1)
