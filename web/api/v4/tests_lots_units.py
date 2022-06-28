import datetime
from django.test import TestCase
from django.urls import reverse
from django.db.models import Count
from django.contrib.auth import get_user_model

from core.models import CarbureLot, CarbureStock, MatierePremiere, Biocarburant, Pays, Entity, ProductionSite, Depot, UserRights
from api.v3.common.urls import urlpatterns
from django_otp.plugins.otp_email.models import EmailDevice
from api.v4.tests_utils import get_lot


class LotsTestUnits(TestCase):
    fixtures = [
        'json/biofuels.json',
        'json/feedstock.json',
        'json/countries.json',
        'json/depots.json',
        'json/entities.json',
        'json/productionsites.json',
    ]


    def setUp(self):
        user_model = get_user_model()
        # let's create a user
        self.password = 'totopouet'
        self.user1 = user_model.objects.create_user(email='testuser1@toto.com', name='Le Super Testeur 1', password=self.password)
        loggedin = self.client.login(username=self.user1.email, password=self.password)
        self.assertTrue(loggedin)

        self.producer = Entity.objects.filter(entity_type=Entity.PRODUCER).annotate(psites=Count('productionsite')).filter(psites__gt=0)[0]
        self.trader = Entity.objects.filter(entity_type=Entity.TRADER)[0]
        self.trader.default_certificate = "TRADER_CERTIFICATE"
        self.trader.save()
        self.operator = Entity.objects.filter(entity_type=Entity.OPERATOR)[0]
        UserRights.objects.update_or_create(entity=self.producer, user=self.user1, role=UserRights.RW)
        UserRights.objects.update_or_create(entity=self.trader, user=self.user1, role=UserRights.RW)
        UserRights.objects.update_or_create(entity=self.operator, user=self.user1, role=UserRights.RW)

        # pass otp verification
        response = self.client.post(reverse('api-v4-request-otp'))
        self.assertEqual(response.status_code, 200)
        device, created = EmailDevice.objects.get_or_create(user=self.user1)
        response = self.client.post(reverse('api-v4-verify-otp'), {'otp_token': device.token})
        self.assertEqual(response.status_code, 200)

    def create_draft(self, lot=None, **kwargs):
        if lot is None:
            lot = get_lot(self.producer)
            del lot['volume']
        lot.update(kwargs)
        response = self.client.post(reverse('api-v4-add-lots'), lot)
        self.assertEqual(response.status_code, 200)
        data = response.json()['data']
        lot_id = data['id']
        lot = CarbureLot.objects.get(id=lot_id)
        return lot

    def test_create_legacy(self):
        lot = self.create_draft(lot=None, volume=1000)
        self.assertEqual(lot.lot_status, CarbureLot.DRAFT)
        self.assertEqual(lot.volume, 1000)

    def test_create_kilogram(self):
        lot = self.create_draft(lot=None, unit='kilogram', amount=1000)
        self.assertEqual(lot.lot_status, CarbureLot.DRAFT)
        self.assertEqual(lot.weight, 1000)

    def test_create_liters(self):
        lot = self.create_draft(lot=None, unit='liter', amount=1000)
        self.assertEqual(lot.lot_status, CarbureLot.DRAFT)
        self.assertEqual(lot.volume, 1000)
        
    def test_create_pci(self):
        lot = self.create_draft(lot=None, unit='lhv', amount=1000)
        self.assertEqual(lot.lot_status, CarbureLot.DRAFT)
        self.assertEqual(lot.lhv_amount, 1000)