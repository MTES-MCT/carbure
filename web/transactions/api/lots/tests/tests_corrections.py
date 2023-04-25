import datetime
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.db.models import Count

from core.models import CarbureLot, Entity, UserRights
from django_otp.plugins.otp_email.models import EmailDevice
from api.v4.tests_utils import get_lot
from transactions.models import LockedYear
from core.carburetypes import CarbureError


class LotCorrectionTest(TestCase):
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
            email="testuser1@toto.com", name="Le Super Testeur 1", password=self.password
        )
        loggedin = self.client.login(username=self.user1.email, password=self.password)
        self.assertTrue(loggedin)

        self.producer = (
            Entity.objects.filter(entity_type=Entity.PRODUCER)
            .annotate(psites=Count("productionsite"))
            .filter(psites__gt=0)[0]
        )
        self.trader = Entity.objects.filter(entity_type=Entity.TRADER)[0]
        self.trader.default_certificate = "TRADER_CERTIFICATE"
        self.trader.save()
        self.operator = Entity.objects.filter(entity_type=Entity.OPERATOR)[0]
        UserRights.objects.update_or_create(entity=self.producer, user=self.user1, role=UserRights.RW)
        UserRights.objects.update_or_create(entity=self.trader, user=self.user1, role=UserRights.RW)
        UserRights.objects.update_or_create(entity=self.operator, user=self.user1, role=UserRights.RW)

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
        response = self.client.post(reverse("api-v4-add-lots"), lot)
        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        lot_id = data["id"]
        lot = CarbureLot.objects.get(id=lot_id)
        return lot

    def send_lot(self, lot):
        response = self.client.post(reverse("api-v4-send-lots"), {"entity_id": self.producer.id, "selection": [lot.id]})
        self.assertEqual(response.status_code, 200)
        lot = CarbureLot.objects.get(id=lot.id)
        return lot

    def recall_lot(self, lot):
        response = self.client.post(
            reverse("api-v5-transactions-lots-request-fix"), {"entity_id": self.producer.id, "lot_ids": [lot.id]}
        )
        self.assertEqual(response.status_code, 200)
        lot = CarbureLot.objects.get(id=lot.id)
        return lot

    def test_recall_and_update(self):
        lotdata = get_lot(entity=self.producer)
        lot = self.create_draft(lot=lotdata)
        lot = self.send_lot(lot)
        self.assertEqual(lot.correction_status, CarbureLot.NO_PROBLEMO)
        self.assertEqual(lot.lot_status, CarbureLot.PENDING)
        lot = self.recall_lot(lot)
        self.assertEqual(lot.correction_status, CarbureLot.IN_CORRECTION)
        self.assertEqual(lot.lot_status, CarbureLot.PENDING)
        lotdata["lot_id"] = lot.id
        lotdata["volume"] = 42000
        response = self.client.post(reverse("api-v4-update-lot"), lotdata)
        self.assertEqual(response.status_code, 200)
        lot = CarbureLot.objects.get(id=lot.id)
        self.assertEqual(lot.volume, 42000)

    def test_simple_correction(self):
        LockedYear.objects.create(year=2020, locked=True)

        lotdata = get_lot(entity=self.producer)
        lot = self.create_draft(lot=lotdata, carbure_client_id=self.trader.id)
        lot = self.send_lot(lot)
        self.assertEqual(lot.lot_status, CarbureLot.PENDING)
        self.assertEqual(lot.correction_status, CarbureLot.NO_PROBLEMO)
        # client requests correction
        response = self.client.post(
            reverse("api-v5-transactions-lots-request-fix"), {"entity_id": self.trader.id, "lot_ids": [lot.id]}
        )
        self.assertEqual(response.status_code, 200)
        lot = CarbureLot.objects.get(id=lot.id)
        self.assertEqual(lot.lot_status, CarbureLot.PENDING)
        self.assertEqual(lot.correction_status, CarbureLot.IN_CORRECTION)
        # we update
        lotdata["lot_id"] = lot.id
        lotdata["volume"] = 42000
        response = self.client.post(reverse("api-v4-update-lot"), lotdata)
        self.assertEqual(response.status_code, 200)
        lot = CarbureLot.objects.get(id=lot.id)
        self.assertEqual(lot.volume, 42000)
        # and mark as fixed
        response = self.client.post(
            reverse("api-v5-transactions-lots-submit-fix"), {"entity_id": self.producer.id, "lot_ids": [lot.id]}
        )
        self.assertEqual(response.status_code, 200)
        lot = CarbureLot.objects.get(id=lot.id)
        self.assertEqual(lot.correction_status, CarbureLot.FIXED)
        # as client, accept fix
        response = self.client.post(
            reverse("api-v5-transactions-lots-approve-fix"), {"entity_id": self.trader.id, "lot_ids": [lot.id]}
        )
        self.assertEqual(response.status_code, 200)
        lot = CarbureLot.objects.get(id=lot.id)
        self.assertEqual(lot.correction_status, CarbureLot.NO_PROBLEMO)
        self.assertEqual(lot.lot_status, CarbureLot.PENDING)
        # finally, accept lot
        response = self.client.post(
            reverse("api-v4-accept-in-stock"), {"entity_id": self.trader.id, "selection": [lot.id]}
        )
        self.assertEqual(response.status_code, 200)
        lot = CarbureLot.objects.get(id=lot.id)
        self.assertEqual(lot.correction_status, CarbureLot.NO_PROBLEMO)
        self.assertEqual(lot.lot_status, CarbureLot.ACCEPTED)

    def test_simple_correction_on_locked_year(self):
        lotdata = get_lot(entity=self.producer)
        lot = self.create_draft(lot=lotdata, carbure_client_id=self.trader.id)
        lot = self.send_lot(lot)
        # # client requests correction
        LockedYear.objects.create(year=2021, locked=True)
        response = self.client.post(
            reverse("api-v5-transactions-lots-request-fix"), {"entity_id": self.trader.id, "lot_ids": [lot.id]}
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["status"], "error")
        self.assertEqual(response.json()["error"], CarbureError.YEAR_LOCKED)

    def test_cascading_correction_trading(self):
        pass

    def test_cascading_correction_stock(self):
        pass
