import datetime
import random
import json
from typing import Generic
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.db.models import Count

from core.models import (
    CarbureLot,
    CarbureStock,
    GenericError,
    MatierePremiere,
    Biocarburant,
    Pays,
    Entity,
    ProductionSite,
    Depot,
    UserRights,
)
from api.v3.common.urls import urlpatterns
from django_otp.plugins.otp_email.models import EmailDevice
from api.v4.tests_utils import get_lot


def debug_errors(lot):
    errors = GenericError.objects.filter(lot=lot)
    for e in errors:
        print(e.error, e.field, e.value, e.extra)


class StocksFlowTest(TestCase):
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
        self.depots = Depot.objects.all()

        # pass otp verification
        response = self.client.post(reverse("api-v4-request-otp"))
        self.assertEqual(response.status_code, 200)
        device, created = EmailDevice.objects.get_or_create(user=self.user1)
        response = self.client.post(reverse("api-v4-verify-otp"), {"otp_token": device.token})
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
