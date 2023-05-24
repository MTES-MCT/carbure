import datetime
from django.test import TestCase
from django.urls import reverse
from django.db.models import Count
from django.contrib.auth import get_user_model

from core.models import CarbureLot, Entity, UserRights
from django_otp.plugins.otp_email.models import EmailDevice
from transactions.api.lots.tests.tests_utils import get_lot


class LotsCertifMayhemTest(TestCase):
    fixtures = [
        "json/biofuels.json",
        "json/feedstock.json",
        "json/countries.json",
        "json/depots.json",
        "json/entities.json",
        "json/productionsites.json",
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
        self.producer.default_certificate = "PRODUCER_CERTIFICATE"
        self.producer.save()

        self.trader = Entity.objects.get(
            pk=18
        )  #  .filter(entity_type=Entity.TRADER)[0]
        self.trader.default_certificate = "TRADER_CERTIFICATE"
        self.trader.save()
        self.operator = Entity.objects.get(
            pk=1
        )  # .filter(entity_type=Entity.OPERATOR)[0]
        UserRights.objects.update_or_create(
            entity=self.producer, user=self.user1, role=UserRights.RW
        )
        UserRights.objects.update_or_create(
            entity=self.trader, user=self.user1, role=UserRights.RW
        )
        UserRights.objects.update_or_create(
            entity=self.operator, user=self.user1, role=UserRights.RW
        )

        # pass otp verification
        response = self.client.post(reverse("auth-request-otp"))
        self.assertEqual(response.status_code, 200)
        device, created = EmailDevice.objects.get_or_create(user=self.user1)
        response = self.client.post(
            reverse("auth-verify-otp"), {"otp_token": device.token}
        )
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

    def send_lot(self, lot, expected_status=200):
        response = self.client.post(
            reverse("transactions-lots-send"),
            {"entity_id": self.producer.id, "selection": [lot.id]},
        )
        if response.status_code != 200:
            print(response.json())
        self.assertEqual(response.status_code, expected_status)
        lot = CarbureLot.objects.get(id=lot.id)
        return lot

    # Cas normal: Mon Certificat = 'supplier_certificate'
    # Cas "trading": Certificat du fournisseur = 'supplier_certificate', mon certificat = 'vendor_certificate'
    def test_send_lot_without_certificate(self):
        # producer to operator, will use entity.default_certificate
        lot = self.create_draft()
        lot = self.send_lot(lot)
        self.assertEqual(lot.supplier_certificate, self.producer.default_certificate)
        self.assertEqual(lot.vendor_certificate, None)

    def test_send_lot_with_supplier_certificate(self):
        # producer to operator, will use what is provided
        lot = self.create_draft(supplier_certificate="TOTO")
        lot = self.send_lot(lot)
        self.assertEqual(lot.supplier_certificate, "TOTO")
        self.assertEqual(lot.vendor_certificate, None)

    def test_send_lot_with_vendor_certificate(self):
        # TRADING - trading lot with no supplier certificate provided
        lot = self.create_draft(
            production_site_commissioning_date="12/12/2012",
            vendor_certificate="TOTO",
            carbure_producer="",
            carbure_production_site="",
            unknown_producer="BIOFUEL GMBH",
        )
        self.assertEqual(lot.supplier_certificate, "")
        self.assertEqual(lot.vendor_certificate, "TOTO")
        lot = self.send_lot(lot)
        child = CarbureLot.objects.get(parent_lot=lot)
        self.assertEqual(child.supplier_certificate, "TOTO")
        self.assertEqual(child.vendor_certificate, None)

    def test_send_lot_with_both_certificates(self):
        # TRADING - both certificates
        lot = self.create_draft(
            production_site_commissioning_date="12/12/2012",
            vendor_certificate="MY_CERTIFICATE",
            supplier_certificate="MY_SUPPLIER",
            carbure_producer="",
            carbure_production_site="",
            unknown_producer="BIOFUEL GMBH",
        )
        self.assertEqual(lot.supplier_certificate, "MY_SUPPLIER")
        self.assertEqual(lot.vendor_certificate, "MY_CERTIFICATE")
        lot = self.send_lot(lot)
        child = CarbureLot.objects.get(parent_lot=lot)
        self.assertEqual(child.supplier_certificate, "MY_CERTIFICATE")
        self.assertEqual(child.vendor_certificate, None)
