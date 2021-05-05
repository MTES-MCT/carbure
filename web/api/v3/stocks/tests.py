from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
import datetime
import random


from core.models import Entity, UserRights
from core.models import Pays, Depot, Biocarburant, MatierePremiere
from core.models import LotV2, LotV2Error
from core.models import LotTransaction, TransactionError
from core.models import LotValidationError

from producers.models import ProductionSite
from django_otp.plugins.otp_email.models import EmailDevice


from api.v3.admin.urls import urlpatterns

def get_random_dae():
    today = datetime.date.today()
    return 'TEST%dFR0000%d' % (today.year, random.randint(100000, 900000))

def debug_lots(valid=False):
    lots = LotV2.objects.all()
    if valid:
        lots = lots.filter(status='Validated')
    for lot in lots:
        print(lot.natural_key())


def debug_transactions(valid=False):
    txs = LotTransaction.objects.all()
    if valid:
        txs = txs.filter(lot__status='Validated')
    for tx in txs:
        print(tx.natural_key())


def debug_errors():
    # debug start
    lot_errors = LotV2Error.objects.all()
    for error in lot_errors:
        print(error.natural_key())
    tx_errors = TransactionError.objects.all()
    for error in tx_errors:
        print(error.natural_key())            
    val_errors = LotValidationError.objects.all()
    for error in val_errors:
        print(error.natural_key())            
    # debug end


class StockAPITest(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.admin_email = 'superadmin@carbure.beta.gouv.fr'
        self.admin_password = 'toto'
        self.fake_admin_email = 'fakeadmin@carbure.beta.gouv.fr'
        self.fake_admin_password = 'toto'

        self.admin_user = user_model.objects.create_user(email=self.admin_email, name='Super Admin', password=self.admin_password, is_staff=True)
        self.fake_admin_user = user_model.objects.create_user(email=self.fake_admin_email, name='Super Admin', password=self.fake_admin_password)

        # let's create a few users
        self.user1 = user_model.objects.create_user(email='testuser1@toto.com', name='Le Super Testeur 1', password=self.fake_admin_password)
        self.user2 = user_model.objects.create_user(email='testuser2@toto.com', name='Le Super Testeur 2', password=self.fake_admin_password)
        self.user3 = user_model.objects.create_user(email='testuser3@toto.com', name='Testeur 3', password=self.fake_admin_password)

        # a few entities
        self.entity1, _ = Entity.objects.update_or_create(name='Le Super Producteur 1', entity_type='Producteur')
        self.entity2, _ = Entity.objects.update_or_create(name='Le Super Producteur 2', entity_type='Producteur')
        self.entity3, _ = Entity.objects.update_or_create(name='Le Super Administrateur 1', entity_type='Administrateur')
        self.entity4, _ = Entity.objects.update_or_create(name='Le Super Operateur 1', entity_type='Opérateur')
        self.entity5, _ = Entity.objects.update_or_create(name='Le Super Trader 1', entity_type='Trader')        

        # some rights
        UserRights.objects.update_or_create(user=self.user1, entity=self.entity1)
        UserRights.objects.update_or_create(user=self.user1, entity=self.entity2)
        UserRights.objects.update_or_create(user=self.user1, entity=self.entity3)
        UserRights.objects.update_or_create(user=self.user2, entity=self.entity2)
        UserRights.objects.update_or_create(user=self.user3, entity=self.entity4)

        # other stuff (production sites, depots, certificates...)
        france, created = Pays.objects.get_or_create(code_pays='FR')
        eth, _ = Biocarburant.objects.get_or_create(code='ETH', name='Ethanol')
        ble, _ = MatierePremiere.objects.get_or_create(code='BLE', name='Blay')
        today = datetime.date.today()
        d = {'country': france, 'date_mise_en_service': today, 'site_id':'SIRET XXX',
        'city': 'paris', 'postal_code': '75001', 'manager_name':'Guillaume Caillou', 
        'manager_phone':'0145247000', 'manager_email': 'test@test.net'}
        self.production_site, _ = ProductionSite.objects.update_or_create(producer=self.entity1, name='PSITE1', defaults=d)
        self.depot, _ = Depot.objects.update_or_create(name='Depot Test', depot_id='001', country=france)

        # login + otp verify
        loggedin = self.client.login(username='testuser1@toto.com', password=self.fake_admin_password)
        self.assertTrue(loggedin)          
        # pass otp verification
        response = self.client.get(reverse('otp-verify'))
        self.assertEqual(response.status_code, 200)
        device = EmailDevice.objects.get(user=self.user1)
        response = self.client.post(reverse('otp-verify'), {'otp_token': device.token})
        self.assertEqual(response.status_code, 302)        

    def create_lot(self, **kwargs):
        lot = {
            'supplier_certificate': 'ISCC-TOTO-02',
            'biocarburant_code': 'ETH',
            'matiere_premiere_code': 'BLE',
            'producer': self.entity1.name,
            'production_site': self.production_site.name,
            'volume': 15000,
            'pays_origine_code': 'FR',
            'eec': 1,
            'ep': 5,
            'etd': 12,
            'dae': get_random_dae(),
            'delivery_date': '2020-12-31',
            'client': self.entity2.name,
            'delivery_site': self.depot.depot_id,
            'entity_id': self.entity1.id,
        }
        lot.update(kwargs)
        response = self.client.post(reverse('api-v3-add-lot'), lot)
        self.assertEqual(response.status_code, 200)
        data = response.json()['data']
        tx_id = data['id']
        lot_id = data['lot']['id']
        return tx_id, lot_id

    def get_stock(self, entity_id):
        response = self.client.get(reverse('api-v3-stocks-get'), {'entity_id': entity_id, 'status': 'stock'})
        self.assertEqual(response.status_code, 200)
        return response.json()['data']

    def validate_lots(self, entity_id, txids):
        response = self.client.post(reverse('api-v3-validate-lot'), {'entity_id': entity_id, 'tx_ids': txids})
        self.assertEqual(response.status_code, 200)        
        debug_errors()
        res = response.json()['data']
        self.assertEqual(res['valid'], len(txids))


    # def test_stock_rights(self):
    #     pass

    # def test_create_mac_from_stock(self):
    #     # add lot
    #     # extract to MAC with unknown client
    #     # extract to MAC where client = myself
    #     # ensure MAC does not appear back in stock
    #     pass

    # def test_forward(self):
    #     # trading without storage
    #     # test forward once. OK
    #     # not in stock anymore
    #     # try forward again. KO
    #     pass

    def test_add_my_lot_to_my_stock(self):
        # create a lot where I am the client
        txid, lotid = self.create_lot(client=self.entity1)
        # validate lot
        self.validate_lots(self.entity1.id, [txid])

        # get stock should return one line
        stock = self.get_stock(self.entity1.id)
        lots_in_stock = stock['lots']
        self.assertEqual(len(lots_in_stock), 1)
        
    def test_add_mac_to_my_stock(self):
        # create a lot where I am the client AND is_mac
        txid, lotid = self.create_lot(client=self.entity1, mac="1")
        # validate lot
        self.validate_lots(self.entity1.id, [txid])

        # get stock should return zero lines
        stock = self.get_stock(self.entity1.id)
        lots_in_stock = stock['lots']
        self.assertEqual(len(lots_in_stock), 0)

    def test_extract(self):
        # normal extract

        # mac extract
        pass