import datetime
import random

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from core.models import CarbureLot, CarbureStock, MatierePremiere, Biocarburant, Pays, Entity, ProductionSite, Depot, UserRights
from api.v3.common.urls import urlpatterns
from django_otp.plugins.otp_email.models import EmailDevice
from api.v4.tests_utils import get_lot


class LotsFlowTest(TestCase):
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

        self.producer = Entity.objects.filter(entity_type=Entity.PRODUCER)[0]
        self.trader = Entity.objects.filter(entity_type=Entity.TRADER)[0]
        self.trader.default_certificate = "TRADER_CERTIFICATE"
        self.trader.save()
        self.operator = Entity.objects.filter(entity_type=Entity.OPERATOR)[0]
        UserRights.objects.update_or_create(entity=self.producer, user=self.user1, role=UserRights.RW)
        UserRights.objects.update_or_create(entity=self.trader, user=self.user1, role=UserRights.RW)
        UserRights.objects.update_or_create(entity=self.operator, user=self.user1, role=UserRights.RW)

        # pass otp verification
        device, created = EmailDevice.objects.get_or_create(user=self.user1)
        response = self.client.post(reverse('api-v4-verify-otp'), {'otp_token': device.token})
        self.assertEqual(response.status_code, 302)
        self.depots = Depot.objects.all()

    def create_draft(self, lot=None, **kwargs):
        if lot is None:
            lot = get_lot(self.producer)
        lot.update(kwargs)
        response = self.client.post(reverse('api-v4-add-lots'), lot)
        self.assertEqual(response.status_code, 200)
        data = response.json()['data']
        lot_id = data['id']        
        lot = CarbureLot.objects.get(id=lot_id)
        return lot

    def send_lot(self, lot):
        response = self.client.post(reverse('api-v4-send-lots'), {'entity_id': self.producer.id, 'selection': [lot.id]})
        self.assertEqual(response.status_code, 200)
        lot = CarbureLot.objects.get(id=lot.id)
        return lot
        
    def stock_slit(self, payload):
        response = self.client.post(reverse('api-v4-stock-split'), {'entity_id': self.trader.id, 'payload': payload})
        self.assertEqual(response.status_code, 200)
        data = response.json()['data']
        lot_id = data['id']        
        lot = CarbureLot.objects.get(id=lot_id)
        return lot

    def test_stock_split(self):
        lot = self.create_draft(carbure_client_id=self.producer.id, volume=50000, delivery_type=CarbureLot.STOCK) # assume the producer also manages his stock in CarbuRe
        lot = self.send_lot(lot)
        lot = CarbureLot.objects.get(id=lot.id)
        self.assertEqual(lot.lot_status, CarbureLot.ACCEPTED)
        self.assertEqual(lot.delivery_type, CarbureLot.STOCK)

        today = datetime.date.today().strftime('%d/%m/%Y')
        # 1: split 10000L for export
        payload = {'volume': 10000, 'stock_id': lot.carbure_id, 'delivery_date': today, 'delivery_site_country_id': 'DE', 'delivery_type': 'EXPORT'}
        lot = self.stock_split(payload)
        self.assertEqual(lot.lot_status, CarbureLot.DRAFT)
        self.assertEqual(lot.delivery_type, CarbureLot.EXPORT)

        # 2: split 10000L for RFC
        payload = {'volume': 10000, 'stock_id': lot.carbure_id, 'delivery_date': today, 'delivery_site_country_id': 'FR', 'delivery_type': 'RFC'}
        lot = self.stock_split(payload)
        self.assertEqual(lot.lot_status, CarbureLot.DRAFT)
        self.assertEqual(lot.delivery_type, CarbureLot.RFC)

        # 3: split 10000L for blending
        payload = {'volume': 10000, 'stock_id': lot.carbure_id, 'delivery_date': today, 'delivery_site_country_id': 'FR', 'delivery_type': 'BLENDING', 'transport_document_reference': 'FR-BLENDING-TEST', 'carbure_delivery_site_id': random.choice(self.depots).depot_id, 'carbure_client_id': self.trader.id}
        lot = self.stock_split(payload)
        self.assertEqual(lot.lot_status, CarbureLot.DRAFT)
        self.assertEqual(lot.delivery_type, CarbureLot.BLENDING)

        # 4: split 10000L for carbure_client
        payload = {'volume': 10000, 'stock_id': lot.carbure_id, 'delivery_date': today, 'delivery_site_country_id': 'FR', 'transport_document_reference': 'FR-SPLIT-SEND-TEST', 'carbure_delivery_site_id': random.choice(self.depots).depot_id, 'carbure_client_id': self.operator.id}
        lot = self.stock_split(payload)
        self.assertEqual(lot.lot_status, CarbureLot.DRAFT)
        self.assertEqual(lot.delivery_type, CarbureLot.UNKNOWN)

        # 5: split 10000L for unknown_client
        payload = {'volume': 10000, 'stock_id': lot.carbure_id, 'delivery_date': today, 'delivery_site_country_id': 'DE', 'transport_document_reference': 'FR-BLENDING-TEST', 'unknown_client': "FOREIGN CLIENT"}
        lot = self.stock_split(payload)
        self.assertEqual(lot.lot_status, CarbureLot.DRAFT)
        self.assertEqual(lot.delivery_type, CarbureLot.UNKNOWN)
