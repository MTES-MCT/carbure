from django.contrib.auth import get_user_model
from django.db.models import Count
from django.test import TestCase
from django.urls import reverse
from django_otp.plugins.otp_email.models import EmailDevice

from core.models import CarbureLot, Entity, GenericError, UserRights
from transactions.api.lots.tests.tests_utils import get_lot


class LotGHGTest(TestCase):
    fixtures = [
        "json/biofuels.json",
        "json/feedstock.json",
        "json/countries.json",
        "json/entities.json",
        "json/productionsites.json",
        "json/depots.json",
        "json/ml.json",
    ]

    def setUp(self):
        user_model = get_user_model()
        # let's create a user
        self.password = "totopouet"
        self.user1 = user_model.objects.create_user(
            email="testuser1@toto.com",
            name="Le Super Testeur 1",
            password=self.password,
        )
        loggedin = self.client.login(username=self.user1.email, password=self.password)
        self.assertTrue(loggedin)

        self.producer = (
            Entity.objects.filter(entity_type=Entity.PRODUCER)
            .annotate(psites=Count("productionsite"))
            .filter(psites__gt=0)[0]
        )
        UserRights.objects.update_or_create(entity=self.producer, user=self.user1, role=UserRights.RW)

        # pass otp verification
        response = self.client.post(reverse("auth-request-otp"))
        self.assertEqual(response.status_code, 200)
        device, created = EmailDevice.objects.get_or_create(user=self.user1)
        response = self.client.post(reverse("auth-verify-otp"), {"otp_token": device.token})
        self.assertEqual(response.status_code, 200)

    def create_draft(self, lot=None, **kwargs):
        if lot is None:
            lot = get_lot(self.producer)
        lot.update(kwargs)
        response = self.client.post(reverse("transactions-lots-add"), lot)
        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        lot_id = data["id"]
        lot = CarbureLot.objects.get(id=lot_id)
        return lot

    def send_lot(self, lot):
        response = self.client.post(
            reverse("transactions-lots-send"),
            {"entity_id": self.producer.id, "selection": [lot.id]},
        )
        self.assertEqual(response.status_code, 200)
        lot = CarbureLot.objects.get(id=lot.id)
        return lot

    def test_eec_too_low(self):
        lot = self.create_draft(biofuel_code="ETH", feedstock_code="BETTERAVE", eec=1)
        lot = self.send_lot(lot)
        nb_errors = GenericError.objects.filter(lot_id=lot.id, error="EEC_ANORMAL_LOW").count()
        self.assertEqual(nb_errors, 1)

    def test_eec_too_high(self):
        lot = self.create_draft(biofuel_code="ETH", feedstock_code="BETTERAVE", eec=22)
        lot = self.send_lot(lot)
        nb_errors = GenericError.objects.filter(lot_id=lot.id, error="EEC_ANORMAL_HIGH").count()
        self.assertEqual(nb_errors, 1)

    def test_ep_too_low(self):
        lot = self.create_draft(biofuel_code="EMHV", feedstock_code="COLZA", ep=1)
        lot = self.send_lot(lot)
        nb_errors = GenericError.objects.filter(lot_id=lot.id, error="EP_ANORMAL_LOW").count()
        self.assertEqual(nb_errors, 1)

    def test_ep_too_high(self):
        lot = self.create_draft(biofuel_code="EMHV", feedstock_code="COLZA", ep=32)
        lot = self.send_lot(lot)
        nb_errors = GenericError.objects.filter(lot_id=lot.id, error="EP_ANORMAL_HIGH").count()
        self.assertEqual(nb_errors, 1)

    def test_etd_too_high(self):
        lot = self.create_draft(biofuel_code="ETH", feedstock_code="BETTERAVE", etd=5.1)
        lot = self.send_lot(lot)
        nb_errors = GenericError.objects.filter(lot_id=lot.id, error="ETD_ANORMAL_HIGH").count()
        self.assertEqual(nb_errors, 1)

    def x_test_etd_eu_default(self):
        lot = self.create_draft(biofuel_code="ETH", feedstock_code="BETTERAVE", country_code="FR", etd=2.3)
        lot = self.send_lot(lot)
        nb_errors = GenericError.objects.filter(lot_id=lot.id, error="ETD_EU_DEFAULT_VALUE").count()
        self.assertEqual(nb_errors, 1)

    def test_etd_no_eu_too_high(self):
        lot = self.create_draft(biofuel_code="ETH", feedstock_code="BETTERAVE", country_code="US", etd=0.9)
        lot = self.send_lot(lot)
        nb_errors = GenericError.objects.filter(lot_id=lot.id, error="ETD_NO_EU_TOO_LOW").count()
        self.assertEqual(nb_errors, 1)
