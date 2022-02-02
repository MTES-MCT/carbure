import datetime
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
        response = self.client.post(reverse('api-v4-request-otp'))
        self.assertEqual(response.status_code, 200)
        device, created = EmailDevice.objects.get_or_create(user=self.user1)
        response = self.client.post(reverse('api-v4-verify-otp'), {'otp_token': device.token})
        self.assertEqual(response.status_code, 200)

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

    def test_create_draft(self, **kwargs):
        lot = self.create_draft(**kwargs)
        self.assertEqual(lot.lot_status, CarbureLot.DRAFT)

    def test_update_lot(self):
        lotdata = get_lot(entity=self.producer)
        lot = self.create_draft(lot=lotdata)
        lotdata['lot_id'] = lot.id
        lotdata['volume'] = 42000
        response = self.client.post(reverse('api-v4-update-lot'), lotdata)
        self.assertEqual(response.status_code, 200)
        lot = CarbureLot.objects.get(id=lot.id)
        self.assertEqual(lot.volume, 42000)

    def test_delete_lot(self):
        lot = self.create_draft()
        response = self.client.post(reverse('api-v4-delete-lots'), {'entity_id': self.producer.id, 'selection': [lot.id]})
        self.assertEqual(response.status_code, 200)
        lot = CarbureLot.objects.get(id=lot.id)
        self.assertEqual(lot.lot_status, CarbureLot.DELETED)

        lot = self.send_lot(self.create_draft())
        response = self.client.post(reverse('api-v4-delete-lots'), {'entity_id': self.producer.id, 'selection': [lot.id]}) # cannot delete a lot not in draft
        self.assertEqual(response.status_code, 400)

        lot = self.create_draft()
        response = self.client.post(reverse('api-v4-delete-lots'), {'entity_id': self.trader.id, 'selection': [lot.id]}) # cannot delete someone else's lot
        self.assertEqual(response.status_code, 400)

    def test_duplicate_lot(self):
        lot = self.create_draft()
        response = self.client.post(reverse('api-v4-duplicate-lot'), {'entity_id': self.producer.id, 'lot_id': lot.id})
        self.assertEqual(response.status_code, 200)
        response = self.client.post(reverse('api-v4-duplicate-lot'), {'entity_id': self.trader.id, 'lot_id': lot.id})
        self.assertEqual(response.status_code, 403)

    def test_send(self):
        lot = self.create_draft()
        lot = self.send_lot(lot)
        self.assertEqual(lot.lot_status, CarbureLot.PENDING)
        
    def test_accept_in_stock(self):
        lot = self.create_draft(carbure_client_id=self.trader.id)
        lot = self.send_lot(lot)

        response = self.client.post(reverse('api-v4-accept-in-stock'), {'entity_id': self.trader.id, 'selection': [lot.id]})
        self.assertEqual(response.status_code, 200)
        lot = CarbureLot.objects.get(id=lot.id)
        self.assertEqual(lot.lot_status, CarbureLot.ACCEPTED)
        self.assertEqual(lot.delivery_type, CarbureLot.STOCK)
        stock = CarbureStock.objects.filter(parent_lot=lot).count()
        self.assertEqual(stock, 1)
        

    def test_accept_rfc(self):
        lot = self.create_draft(carbure_client_id=self.operator.id)
        lot = self.send_lot(lot)
        self.assertEqual(lot.lot_status, CarbureLot.PENDING)
        self.assertEqual(lot.delivery_type, CarbureLot.UNKNOWN)    
        response = self.client.post(reverse('api-v4-accept-rfc'), {'entity_id': self.operator.id, 'selection': [lot.id]})
        self.assertEqual(response.status_code, 200)
        lot = CarbureLot.objects.get(id=lot.id)
        self.assertEqual(lot.lot_status, CarbureLot.ACCEPTED)
        self.assertEqual(lot.delivery_type, CarbureLot.RFC)

    def test_send_rfc(self):
        lot = self.create_draft(unknown_client="CLIENT MAC", delivery_type='RFC', carbure_client_id='')
        lot = self.send_lot(lot)
        self.assertEqual(lot.lot_status, CarbureLot.ACCEPTED)
        self.assertEqual(lot.delivery_type, CarbureLot.RFC)    
        
    def test_accept_trading_to_carbure_client(self):
        lot = self.create_draft(carbure_client_id=self.trader.id)
        lot = self.send_lot(lot)
        self.assertEqual(lot.lot_status, CarbureLot.PENDING)
        self.assertEqual(lot.delivery_type, CarbureLot.UNKNOWN)

        response = self.client.post(reverse('api-v4-accept-trading'), {'entity_id': self.trader.id, 'selection': [lot.id], 'client_entity_id': self.operator.id})
        self.assertEqual(response.status_code, 200)
        lot = CarbureLot.objects.get(id=lot.id)
        self.assertEqual(lot.lot_status, CarbureLot.ACCEPTED)
        self.assertEqual(lot.delivery_type, CarbureLot.TRADING)
        child = CarbureLot.objects.get(parent_lot=lot)
        self.assertEqual(child.lot_status, CarbureLot.PENDING)
        self.assertEqual(child.delivery_type, CarbureLot.UNKNOWN)

    def test_accept_trading_to_unknown_client(self):
        lot = self.create_draft(carbure_client_id=self.trader.id)
        lot = self.send_lot(lot)
        self.assertEqual(lot.lot_status, CarbureLot.PENDING)
        self.assertEqual(lot.delivery_type, CarbureLot.UNKNOWN)

        response = self.client.post(reverse('api-v4-accept-trading'), {'entity_id': self.trader.id, 'selection': [lot.id], 'unknown_client': "TRADER CLIENT"})
        self.assertEqual(response.status_code, 200)
        lot = CarbureLot.objects.get(id=lot.id)
        self.assertEqual(lot.lot_status, CarbureLot.ACCEPTED)
        self.assertEqual(lot.delivery_type, CarbureLot.TRADING)
        child = CarbureLot.objects.get(parent_lot=lot)
        self.assertEqual(child.lot_status, CarbureLot.ACCEPTED)
        self.assertEqual(child.delivery_type, CarbureLot.UNKNOWN)

    def test_accept_processing(self):
        lot = self.create_draft(carbure_client_id=self.trader.id)
        lot = self.send_lot(lot)
        self.assertEqual(lot.lot_status, CarbureLot.PENDING)
        self.assertEqual(lot.delivery_type, CarbureLot.UNKNOWN)

        response = self.client.post(reverse('api-v4-accept-processing'), {'entity_id': self.trader.id, 'selection': [lot.id], 'processing_entity_id': self.operator.id})
        self.assertEqual(response.status_code, 200)
        lot = CarbureLot.objects.get(id=lot.id)
        self.assertEqual(lot.lot_status, CarbureLot.ACCEPTED)
        self.assertEqual(lot.delivery_type, CarbureLot.PROCESSING)
        child = CarbureLot.objects.get(parent_lot=lot)
        self.assertEqual(child.lot_status, CarbureLot.PENDING)
        self.assertEqual(child.delivery_type, CarbureLot.UNKNOWN)

    def test_accept_blending(self):
        lot = self.create_draft(carbure_client_id=self.operator.id)
        lot = self.send_lot(lot)
        self.assertEqual(lot.lot_status, CarbureLot.PENDING)
        self.assertEqual(lot.delivery_type, CarbureLot.UNKNOWN)
        response = self.client.post(reverse('api-v4-accept-blending'), {'entity_id': self.operator.id, 'selection': [lot.id]})
        self.assertEqual(response.status_code, 200)
        lot = CarbureLot.objects.get(id=lot.id)
        self.assertEqual(lot.lot_status, CarbureLot.ACCEPTED)
        self.assertEqual(lot.delivery_type, CarbureLot.BLENDING)

    def test_accept_export(self):
        lot = self.create_draft(carbure_client_id=self.operator.id)
        lot = self.send_lot(lot)
        self.assertEqual(lot.lot_status, CarbureLot.PENDING)
        self.assertEqual(lot.delivery_type, CarbureLot.UNKNOWN)
        response = self.client.post(reverse('api-v4-accept-export'), {'entity_id': self.operator.id, 'selection': [lot.id]})
        self.assertEqual(response.status_code, 200)
        lot = CarbureLot.objects.get(id=lot.id)
        self.assertEqual(lot.lot_status, CarbureLot.ACCEPTED)
        self.assertEqual(lot.delivery_type, CarbureLot.EXPORT)

    def test_accept_direct_delivery(self):
        lot = self.create_draft(carbure_client_id=self.operator.id)
        lot = self.send_lot(lot)
        self.assertEqual(lot.lot_status, CarbureLot.PENDING)
        self.assertEqual(lot.delivery_type, CarbureLot.UNKNOWN)
        response = self.client.post(reverse('api-v4-accept-direct-delivery'), {'entity_id': self.operator.id, 'selection': [lot.id]})
        self.assertEqual(response.status_code, 200)
        lot = CarbureLot.objects.get(id=lot.id)
        self.assertEqual(lot.lot_status, CarbureLot.ACCEPTED)
        self.assertEqual(lot.delivery_type, CarbureLot.DIRECT)
