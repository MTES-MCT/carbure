from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
import datetime
import json
import random
import os

from core.models import Entity, UserRights
from core.models import Pays, Depot, Biocarburant, MatierePremiere
from core.models import LotV2, LotTransaction, GenericError

from certificates.models import ISCCCertificate, EntityISCCTradingCertificate

from producers.models import ProductionSite
from django.core.files.uploadedfile import SimpleUploadedFile
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
    lot_errors = GenericError.objects.all()
    for error in lot_errors:
        print(error.natural_key())         
    # debug end


class StockAPITest(TestCase):
    home = os.environ['CARBURE_HOME']
    fixtures = ['{home}/web/fixtures/json/countries.json'.format(home=home), 
    '{home}/web/fixtures/json/feedstock.json'.format(home=home), 
    '{home}/web/fixtures/json/biofuels.json'.format(home=home),
    '{home}/web/fixtures/json/depots.json'.format(home=home)]

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
        UserRights.objects.update_or_create(user=self.user1, entity=self.entity1, role='RW')
        UserRights.objects.update_or_create(user=self.user1, entity=self.entity2, role='RW')
        UserRights.objects.update_or_create(user=self.user1, entity=self.entity3, role='RW')
        UserRights.objects.update_or_create(user=self.user2, entity=self.entity2, role='RW')
        UserRights.objects.update_or_create(user=self.user3, entity=self.entity4, role='RW')

        # other stuff (production sites, depots, certificates...)
        france, created = Pays.objects.get_or_create(code_pays='FR')
        today = datetime.date.today()
        d = {'country': france, 'date_mise_en_service': today, 'site_id':'SIRET XXX',
        'city': 'paris', 'postal_code': '75001', 'manager_name':'Guillaume Caillou', 
        'manager_phone':'0145247000', 'manager_email': 'test@test.net'}
        self.production_site, _ = ProductionSite.objects.update_or_create(producer=self.entity1, name='PSITE1', defaults=d)
        self.depot, _ = Depot.objects.update_or_create(name='Depot Test', depot_id='001', country=france)
        self.depot2, _ = Depot.objects.update_or_create(name='Depot Test 2', depot_id='002', country=france)

        # login + otp verify
        loggedin = self.client.login(username='testuser1@toto.com', password=self.fake_admin_password)
        self.assertTrue(loggedin)          
        # pass otp verification
        response = self.client.get(reverse('otp-verify'))
        self.assertEqual(response.status_code, 200)
        device = EmailDevice.objects.get(user=self.user1)
        response = self.client.post(reverse('otp-verify'), {'otp_token': device.token})
        self.assertEqual(response.status_code, 302)        

    def login_as(self, entity):
        # get user with rights to entity
        rights = UserRights.objects.filter(entity=entity)
        if rights.count() > 0:
            right = rights[0]
            # login + otp verify
            loggedin = self.client.login(username=right.user.email, password=self.fake_admin_password)
            self.assertTrue(loggedin)          
            # pass otp verification
            response = self.client.get(reverse('otp-verify'))
            self.assertEqual(response.status_code, 200)
            device = EmailDevice.objects.get(user=right.user)
            response = self.client.post(reverse('otp-verify'), {'otp_token': device.token})
            self.assertEqual(response.status_code, 302)                  
            return True
        else:
            return False
          

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

    def get_stock(self, entity_id, status='stock', show_empty='0'):
        response = self.client.get(reverse('api-v3-stocks-get'), {'entity_id': entity_id, 'status': status, 'show_empty': show_empty})
        self.assertEqual(response.status_code, 200)
        return response.json()['data']

    def validate_lots(self, entity_id, txids):
        response = self.client.post(reverse('api-v3-validate-lot'), {'entity_id': entity_id, 'tx_ids': txids})
        self.assertEqual(response.status_code, 200)        
        debug_errors()
        res = response.json()['data']
        self.assertEqual(res['valid'], len(txids))


    def create_draft(self, **kwargs):
        draft = {
            'tx_id': None,
            'volume': None,
            'dae': 'blablabla',
            'client': self.entity2.name,
            'mac': '',
            'delivery_site_country': '',
            'dae': get_random_dae(),
            'delivery_date': '2020-12-31',
            'delivery_site': self.depot.depot_id,
            'entity_id': self.entity1.id,
        }
        draft.update(kwargs)
        drafts = [draft]
        response = self.client.post(reverse('api-v3-stocks-create-drafts'), {'entity_id': self.entity1.id, 'drafts': json.dumps(drafts)})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        return data

    def create_draft_from_match(self, **kwargs):
        draft = {
            'volume': None,
            'dae': 'blablabla',
            'client': self.entity2.name,
            'delivery_site_country': '',
            'dae': get_random_dae(),
            'delivery_date': '2020-12-31',
            'delivery_site': self.depot.depot_id,
            'entity_id': self.entity1.id,
        }
        draft.update(kwargs)
        drafts = [draft]
        response = self.client.post(reverse('api-v3-stocks-create-drafts'), {'entity_id': self.entity1.id, 'drafts': json.dumps(drafts)})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        return data

    def send_stock_drafts(self, entity_id, txids, expectedstatus=200):
        response = self.client.post(reverse('api-v3-stocks-send-drafts'), {'entity_id': entity_id, 'tx_ids': txids})
        self.assertEqual(response.status_code, expectedstatus)
        return response.json()

    def accept_pending_lots(self, entity_id, txids, expectedstatus=200):
        response = self.client.post(reverse('api-v3-accept-lot'), {'entity_id': entity_id, 'tx_ids': txids})
        self.assertEqual(response.status_code, expectedstatus)
        return response.json()

    def forward_stock_tx(self, entity_id, txids, recipient, expectedstatus=200):
        entity = Entity.objects.get(id=entity_id)
        today = datetime.date.today()
        certificate, _ = ISCCCertificate.objects.get_or_create(certificate_id='CERTIF', certificate_holder='Das Zuper Produktor', addons='was is das', valid_from=today, valid_until=today)
        EntityISCCTradingCertificate.objects.update_or_create(certificate=certificate, entity=entity)
        response = self.client.post(reverse('api-v3-stocks-forward'), {'entity_id': entity_id, 'tx_ids': txids, 'recipient': recipient, 'certificate_id': certificate.certificate_id})
        self.assertEqual(response.status_code, expectedstatus)
        return response.json()

    def test_stock_rights(self):
        self.login_as(self.entity1)
        # create a lot as entity1 with client entity2
        txid, lotid = self.create_lot(client=self.entity5)
        # validate lot
        self.validate_lots(self.entity1.id, [txid])
        # accept it (logged in as entity1)
        self.accept_pending_lots(self.entity5.id, [txid], 403)

    def test_extract(self):
        # create a lot where I am the client
        txid, lotid = self.create_lot(client=self.entity1)
        # validate lot
        self.validate_lots(self.entity1.id, [txid])

        tx = LotTransaction.objects.get(id=txid)
        self.assertEqual(tx.lot.remaining_volume, tx.lot.volume)
        # create draft (extract)
        volume = round(tx.lot.volume / 4, 2)
        draft = self.create_draft(tx_id=tx.id, volume=volume, client=self.entity2.name, delivery_site=self.depot2.depot_id)
        draft_tx = LotTransaction.objects.get(parent_tx=tx)

        # volumes are unchanged 
        tx = LotTransaction.objects.get(id=txid)
        self.assertEqual(tx.lot.remaining_volume, tx.lot.volume)
        self.assertEqual(draft_tx.lot.remaining_volume, draft_tx.lot.volume)
        self.assertEqual(draft_tx.lot.volume, volume)

        # send it
        self.send_stock_drafts(self.entity1.id, [draft_tx.id])

        # volumes have changed
        tx = LotTransaction.objects.get(id=txid)
        child_tx = LotTransaction.objects.get(parent_tx=tx)

        self.assertEqual(tx.lot.remaining_volume, tx.lot.volume - volume)
        self.assertEqual(tx.lot.remaining_volume + child_tx.lot.volume, tx.lot.volume)
        self.assertEqual(child_tx.lot.remaining_volume, child_tx.lot.volume)
        self.assertEqual(child_tx.lot.volume, volume)


    def test_create_mac_from_stock(self):
        # create a lot where I am the client
        volume = 50000
        txid, lotid = self.create_lot(client=self.entity1, biocarburant_code="ED95", volume=volume)
        # validate lot
        self.validate_lots(self.entity1.id, [txid])
        # it should now be in my stock
        lot_stock = LotTransaction.objects.get(id=txid)
        self.assertEqual(lot_stock.is_stock, True)
        self.assertEqual(lot_stock.lot.volume, volume)
        self.assertEqual(lot_stock.lot.remaining_volume, volume)
        self.assertEqual(lot_stock.delivery_status, 'A')
        self.assertEqual(lot_stock.lot.status, 'Validated')



        # create draft (extract)
        stock_source = LotTransaction.objects.get(id=txid)
        drafts = self.create_draft(tx_id=stock_source.id, volume=25000, client=self.entity2.name, delivery_site=self.depot2.depot_id, mac='true')
        new_draft_id = drafts['data']['tx_ids'][0]
        draft_tx = LotTransaction.objects.get(id=new_draft_id)
        # extract is still a draft, ensure parent tx not affected
        stock_source = LotTransaction.objects.get(id=txid)
        self.assertEqual(stock_source.lot.volume, 50000) # volume unaffected
        self.assertEqual(stock_source.lot.remaining_volume, 50000) # remaining volume unaffected

        # send it
        res = self.send_stock_drafts(self.entity1.id, [draft_tx.id])
        # ensure it's flagged as a MAC
        draft_tx = LotTransaction.objects.get(id=draft_tx.id)
        self.assertEqual(draft_tx.is_mac, True)
        self.assertEqual(draft_tx.delivery_status, 'N')
        self.assertEqual(draft_tx.lot.volume, 25000)
        # check parent tx volumes
        stock_source = LotTransaction.objects.get(id=txid)
        self.assertEqual(stock_source.lot.volume, 50000) # volume unaffected
        self.assertEqual(stock_source.lot.remaining_volume, 25000) # remaining volume reduced


        # create another one, from the same original lot
        # extract to MAC with unknown client
        drafts = self.create_draft(tx_id=stock_source.id, volume=10000, client="garage bonlieu", delivery_site="", mac='true')
        new_draft_id = drafts['data']['tx_ids'][0]
        draft_tx = LotTransaction.objects.get(id=new_draft_id)
        self.assertEqual(draft_tx.lot.status, 'Draft')
        self.assertEqual(draft_tx.delivery_status, 'N')
        # send it
        self.send_stock_drafts(self.entity1.id, [draft_tx.id])
        draft_tx = LotTransaction.objects.get(id=new_draft_id)
        self.assertEqual(draft_tx.delivery_status, 'A')
        self.assertEqual(draft_tx.is_mac, True)

        stock_source = LotTransaction.objects.get(id=txid)
        self.assertEqual(stock_source.lot.volume, 50000) # volume unaffected
        self.assertEqual(stock_source.lot.remaining_volume, 15000) # remaining volume reduced

        # extract to MAC where client = myself
        drafts = self.create_draft(tx_id=stock_source.id, volume=15000, client=self.entity1.name, delivery_site="MAC", mac='true')
        new_draft_id = drafts['data']['tx_ids'][0]
        draft_tx = LotTransaction.objects.get(id=new_draft_id)
        # send
        self.send_stock_drafts(self.entity1.id, [draft_tx.id])
        draft_tx = LotTransaction.objects.get(id=new_draft_id)
        self.assertEqual(draft_tx.delivery_status, 'A')
        self.assertEqual(draft_tx.is_mac, True)
        stock_source = LotTransaction.objects.get(id=txid)
        self.assertEqual(stock_source.lot.volume, 50000) # volume unaffected
        self.assertEqual(stock_source.lot.remaining_volume, 0) # remaining volume reduced

        # ensure MAC does not appear back in stock
        self.assertEqual(draft_tx.is_stock, False)
        stock = self.get_stock(self.entity1.id)
        lots_in_stock = stock['lots']
        # 0 lots in stock (mac is not coming back to stock and source_tx entirely consumed)
        self.assertEqual(len(lots_in_stock), 0)


    def test_forward(self):
        # trading without storage
        # create a lot as entity1 (producer) and send it to entity2 (trader)
        txid, lotid = self.create_lot(client=self.entity2)
        # validate lot
        self.validate_lots(self.entity1.id, [txid])

        # it should now be pending acceptation by entity2
        self.login_as(self.entity2)
        stock = self.get_stock(self.entity2.id, status='in')
        pending_txs = stock['lots']
        self.assertEqual(len(pending_txs), 1)

        # accept it
        txid = pending_txs[0]['id']
        self.accept_pending_lots(self.entity2.id, [txid])
        tx = LotTransaction.objects.get(id=txid)
        # check status has changed
        self.assertEqual(tx.delivery_status, 'A')
        self.assertEqual(tx.is_stock, True)

        # test forward once. OK
        forwarded = self.forward_stock_tx(self.entity2.id, [txid], self.entity3.id)
        # not in stock anymore
        stock = self.get_stock(self.entity2.id)
        self.assertEqual(len(stock['lots']), 0)

        # 
        nbchild = LotTransaction.objects.filter(parent_tx_id=txid).count()
        self.assertEqual(nbchild, 1)
        # try forward again. KO
        self.forward_stock_tx(self.entity3.id, [txid], self.entity3.id, 400)
        nbchild = LotTransaction.objects.filter(parent_tx_id=txid).count()
        self.assertEqual(nbchild, 1)


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
        txid, lotid = self.create_lot(client=self.entity1, mac="true")
        # validate lot
        self.validate_lots(self.entity1.id, [txid])

        # get stock should return zero lines
        stock = self.get_stock(self.entity1.id)
        lots_in_stock = stock['lots']
        self.assertEqual(len(lots_in_stock), 0)

    def test_extract_more_than_stock(self):
        # create a lot where I am the client
        txid, lotid = self.create_lot(client=self.entity1)
        # validate lot
        self.validate_lots(self.entity1.id, [txid])
        tx = LotTransaction.objects.get(id=txid)
        self.assertEqual(tx.lot.status, LotV2.VALIDATED)
        self.assertEqual(tx.delivery_status, LotTransaction.ACCEPTED)
        # extract 
        drafts = self.create_draft(tx_id=tx.id, volume=tx.lot.volume + 1, client=self.entity2.name, delivery_site="osef", delivery_site_country='DE')
        new_draft_id = drafts['data']['tx_ids'][0]
        draft_tx = LotTransaction.objects.get(id=new_draft_id)
        self.send_stock_drafts(self.entity1.id, [draft_tx.id], expectedstatus=400)

    def test_stock_matching_engine(self):
        # check MP rule
        # create many lots
        txid, lotid = self.create_lot(client=self.entity1, biocarburant_code='ETH', matiere_premiere_code='BLE', pays_origine_code='FR')
        txid2, lotid = self.create_lot(client=self.entity1, biocarburant_code='ETH', matiere_premiere_code='MAIS', pays_origine_code='FR')
        txid3, lotid = self.create_lot(client=self.entity1, biocarburant_code='ETH', matiere_premiere_code='BLE', pays_origine_code='DE')
        txid4, lotid = self.create_lot(client=self.entity1, biocarburant_code='ED95', matiere_premiere_code='BLE', pays_origine_code='FR')

        txid5, lotid = self.create_lot(client=self.entity1, biocarburant_code='EMHV', matiere_premiere_code='COLZA', pays_origine_code='FR', delivery_site='001')
        txid6, lotid = self.create_lot(client=self.entity1, biocarburant_code='EMHV', matiere_premiere_code='COLZA', pays_origine_code='FR', delivery_site='002')
        self.validate_lots(self.entity1.id, [txid, txid2, txid3, txid4, txid5, txid6])

        # create draft matching with various matching rules
        drafts = self.create_draft_from_match(biocarburant_code='ED95', volume=1000, client=self.entity2.name, delivery_site="osef")
        drafts = self.create_draft_from_match(biocarburant_code='ETH', matiere_premiere_code='MAIS', volume=1000, client=self.entity2.name, delivery_site="osef")
        drafts = self.create_draft_from_match(pays_origine_code='DE', volume=1000, client=self.entity2.name, delivery_site="osef")
        drafts = self.create_draft_from_match(biocarburant_code='EMHV', depot='001', volume=1000, client=self.entity2.name, delivery_site="osef")


    def test_upload_template(self):
        # create a few lots
        txid, lotid = self.create_lot(client=self.entity1, biocarburant_code='ETH', matiere_premiere_code='BLE', pays_origine_code='FR')
        txid2, lotid = self.create_lot(client=self.entity1, biocarburant_code='ETH', matiere_premiere_code='MAIS', pays_origine_code='FR')
        txid3, lotid = self.create_lot(client=self.entity1, biocarburant_code='ETH', matiere_premiere_code='BLE', pays_origine_code='DE')
        txid4, lotid = self.create_lot(client=self.entity1, biocarburant_code='ED95', matiere_premiere_code='BLE', pays_origine_code='FR')

        txid5, lotid = self.create_lot(client=self.entity1, biocarburant_code='EMHV', matiere_premiere_code='COLZA', pays_origine_code='FR', delivery_site='001')
        txid6, lotid = self.create_lot(client=self.entity1, biocarburant_code='EMHV', matiere_premiere_code='COLZA', pays_origine_code='FR', delivery_site='002')
        self.validate_lots(self.entity1.id, [txid, txid2, txid3, txid4, txid5, txid6])
        # download template-stock
        response = self.client.get(reverse('api-v3-template-mass-balance'), {'entity_id': self.entity1.id})
        self.assertEqual(response.status_code, 200)
        filecontent = response.content
        # upload simple template
        f = SimpleUploadedFile("template.xslx", filecontent)
        response = self.client.post(reverse('api-v3-upload-mass-balance'), {'entity_id': self.entity1.id, 'file': f})
        self.assertEqual(response.status_code, 200)

        # download model 2
        response = self.client.get(reverse('api-v3-template-mass-balance-bcghg'), {'entity_id': self.entity3.id})
        self.assertEqual(response.status_code, 200)

        # upload model 2 template
        f = SimpleUploadedFile("template.xslx", filecontent)
        response = self.client.post(reverse('api-v3-upload-mass-balance'), {'entity_id': self.entity1.id, 'file': f})
        self.assertEqual(response.status_code, 200)

        # we should have a few drafts
        stock_drafts = self.get_stock(self.entity1.id, status='tosend')
        self.assertEqual(len(stock_drafts['lots']), 20)


    def test_show_empty_stock(self):
        # create a lot where I am the client
        txid, lotid = self.create_lot(client=self.entity1)
        # validate lot
        self.validate_lots(self.entity1.id, [txid])

        # get stock should return one line
        stock = self.get_stock(self.entity1.id)
        lots_in_stock = stock['lots']
        self.assertEqual(len(lots_in_stock), 1)

        # extract volume from lot and send
        stock_tx = LotTransaction.objects.get(id=txid)
        drafts = self.create_draft(tx_id=stock_tx.id, volume=stock_tx.lot.volume, client=self.entity2.name, delivery_site="osef", delivery_site_country='DE')
        new_draft_id = drafts['data']['tx_ids'][0]
        draft_tx = LotTransaction.objects.get(id=new_draft_id)
        self.send_stock_drafts(self.entity1.id, [draft_tx.id])

        # get stock should return zero line
        stock = self.get_stock(self.entity1.id)
        lots_in_stock = stock['lots']
        self.assertEqual(len(lots_in_stock), 0)

        # however adding the flag show_empty='1'' should return 1 line
        stock = self.get_stock(self.entity1.id, show_empty='1')
        lots_in_stock = stock['lots']
        self.assertEqual(len(lots_in_stock), 1)