from django.contrib.auth import get_user_model
from django.db.models import Count
from django.test import TestCase as DjangoTestCase
from django.urls import reverse
from django_otp.plugins.otp_email.models import EmailDevice

from core.models import CarbureLot, Entity, UserRights
from transactions.tests.tests_utils import get_lot


class TestCase(DjangoTestCase):
    fixtures = [
        "json/biofuels.json",
        "json/feedstock.json",
        "json/countries.json",
        "json/depots.json",
        "json/entities.json",
        "json/productionsites.json",
        "json/entities_sites.json",
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
        assert loggedin

        self.created_by = (
            Entity.objects.filter(entity_type=Entity.PRODUCER)
            .annotate(psites=Count("entitysite__site"))
            .filter(psites__gt=0)[0]
        )
        self.trader = Entity.objects.filter(entity_type=Entity.TRADER)[0]
        self.trader.default_certificate = "TRADER_CERTIFICATE"
        self.trader.save()
        self.operator = Entity.objects.filter(entity_type=Entity.OPERATOR)[0]

        
        UserRights.objects.update_or_create(
            entity=self.created_by, user=self.user1, role=UserRights.RW
        )
        UserRights.objects.update_or_create(
            entity=self.trader, user=self.user1, role=UserRights.RW
        )
        UserRights.objects.update_or_create(
            entity=self.operator, user=self.user1, role=UserRights.RW
        )


        # pass otp verification
        response = self.client.post(reverse("auth-request-otp"))
        assert response.status_code == 200
        device, created = EmailDevice.objects.get_or_create(user=self.user1)
        response = self.client.post(
            reverse("auth-verify-otp"), {"otp_token": device.token}
        )
        assert response.status_code == 200

    def create_draft_v2(self, **kwargs):
        lot = get_lot(self.created_by)
        lot.update(kwargs)
        return self.client.post(
            reverse("transactions-lots-add") + f"?entity_id={self.created_by.id}", lot
        )

    def create_draft(self, lot=None, **kwargs):
        if lot is None:
            lot = get_lot(self.created_by)
        lot.update(kwargs)
        response = self.client.post(
            reverse("transactions-lots-add") + f"?entity_id={self.created_by.id}", lot
        )
        assert response.status_code == 200
        data = response.json()
        lot_id = data["id"]
        lot = CarbureLot.objects.get(id=lot_id)
        return lot

    def send_lot(self, lot):
        response = self.client.post(
            reverse("transactions-lots-send") + f"?entity_id={self.created_by.id}",
            {"entity_id": self.created_by.id, "selection": [lot.id]},
        )
        assert response.status_code == 200
        lot = CarbureLot.objects.get(id=lot.id)
        return lot
