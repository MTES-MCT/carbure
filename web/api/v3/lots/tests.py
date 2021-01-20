import datetime
import os
import time
from django.test import TestCase
from django.test import TransactionTestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from core.models import Entity, UserRights, LotV2, LotTransaction, ProductionSite, Pays, Biocarburant, MatierePremiere, Depot, LotValidationError, LotV2Error, TransactionError
from api.v3.admin.urls import urlpatterns
from django_otp.plugins.otp_email.models import EmailDevice


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


class LotsAPITest(TransactionTestCase):
    home = os.environ['CARBURE_HOME']
    fixtures = ['{home}/web/fixtures/json/countries.json'.format(home=home), 
    '{home}/web/fixtures/json/feedstock.json'.format(home=home), 
    '{home}/web/fixtures/json/biofuels.json'.format(home=home),
    '{home}/web/fixtures/json/depots.json'.format(home=home)]

    def setUp(self):
        user_model = get_user_model()
        self.user_email = 'testuser1@toto.com'
        self.user_password = 'totopouet'
        self.user1 = user_model.objects.create_user(email=self.user_email, name='Le Super Testeur 1', password=self.user_password)

        # a few entities
        self.test_producer, _ = Entity.objects.update_or_create(name='Le Super Producteur 1', entity_type='Producteur')
        self.test_operator, _ = Entity.objects.update_or_create(name='OPERATEUR1', entity_type='Opérateur')
        self.entity3, _ = Entity.objects.update_or_create(name='Le Super Trader 1', entity_type='Trader')

        # some rights
        UserRights.objects.update_or_create(user=self.user1, entity=self.test_producer)
        UserRights.objects.update_or_create(user=self.user1, entity=self.test_operator)         
        # note: user1 does not have access to entity3
        france = Pays.objects.get(code_pays='FR')
        today = datetime.date.today()
        d = {'country': france, 'date_mise_en_service': today, 'site_id':'SIRET XXX',
        'city': 'paris', 'postal_code': '75001', 'manager_name':'Guillaume Caillou', 
        'manager_phone':'0145247000', 'manager_email': 'test@test.net'}
        self.production_site, _ = ProductionSite.objects.update_or_create(producer=self.test_producer, name='PSITE1', defaults=d)
        Depot.objects.update_or_create(name='Depot Test', depot_id='001', country=france)

        loggedin = self.client.login(username=self.user_email, password=self.user_password)
        self.assertTrue(loggedin)          
        # pass otp verification
        response = self.client.get(reverse('otp-verify'))
        self.assertEqual(response.status_code, 200)
        device = EmailDevice.objects.get(user=self.user1)
        response = self.client.post(reverse('otp-verify'), {'otp_token': device.token})
        self.assertEqual(response.status_code, 302)

    def upload_file(self, filename, entity):
        print('uploading file %s' % (filename))
        file_directory = '%s/web/fixtures/csv/test_data' % (os.environ['CARBURE_HOME'])
        filepath = '%s/%s' % (file_directory, filename)
        fh = open(filepath, 'rb')
        data = fh.read()
        fh.close()
        f = SimpleUploadedFile("lots.xlsx", data)
        response = self.client.post(reverse('api-v3-upload'), {'entity_id': entity.id, 'file': f})
        if response.status_code != 200:
            print('Failed to upload %s' % (filename))
        self.assertEqual(response.status_code, 200)
        return response.json()

    def ensure_nb_lots(self, nb_lots):
        count = LotV2.objects.all().count()
        self.assertEqual(count, nb_lots)
    
    def ensure_nb_txs(self, nb_txs):
        count = LotTransaction.objects.all().count()
        self.assertEqual(count, nb_txs)

    def ensure_nb_lot_errors(self, nb):
        count = LotV2Error.objects.all().count()
        self.assertEqual(count, nb)

    def ensure_nb_tx_errors(self, nb):
        count = TransactionError.objects.all().count()
        self.assertEqual(count, nb)

    def ensure_nb_sanity_errors(self, nb):
        count = LotValidationError.objects.all().count()
        self.assertEqual(count, nb)

    def test_lot_actions(self):
        # as producer / trader
        dae = 'TEST2020FR00923-094-32094'
        lot = {
            'production_site': self.production_site.name,
            'biocarburant_code': 'ETH',
            'matiere_premiere_code': 'BLE',
            'volume': 15000,
            'pays_origine_code': 'FR',
            'ep': 5,
            'etd': 12,
            'dae': dae,
            'delivery_date': '2020-12-31',
            'client': self.test_operator.name,
            'delivery_site': '001',
            'entity_id': self.test_producer.id,
        }
        # add manual lot
        response = self.client.post(reverse('api-v3-add-lot'), lot)
        self.assertEqual(response.status_code, 200)  
        # update it
        tx = LotTransaction.objects.get(dae=dae)
        lot['ep'] = '6'
        lot['tx_id'] = tx.id
        response = self.client.post(reverse('api-v3-update-lot'), lot)
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('api-v3-lots-get-details'), {'entity_id': self.test_producer.id, 'tx_id': tx.id})
        self.assertEqual(response.status_code, 200)        
        data = response.json()['data']
        self.assertEqual(data['transaction']['lot']['ep'], 6)
        # duplicate 3 times
        response = self.client.post(reverse('api-v3-duplicate-lot'), {'entity_id': self.test_producer.id, 'tx_id': tx.id})
        response = self.client.post(reverse('api-v3-duplicate-lot'), {'entity_id': self.test_producer.id, 'tx_id': tx.id})
        response = self.client.post(reverse('api-v3-duplicate-lot'), {'entity_id': self.test_producer.id, 'tx_id': tx.id})               
        # delete 4th duplicate
        last = LotTransaction.objects.latest('id')
        response = self.client.post(reverse('api-v3-delete-lot'), {'entity_id': self.test_producer.id, 'tx_ids':  [last.id]})
        self.assertEqual(response.status_code, 200)        
        # get drafts, make sure we have 3
        response = self.client.get(reverse('api-v3-lots-get'), {'entity_id': self.test_producer.id, 'status': 'draft', 'year': '2020'})
        self.assertEqual(response.status_code, 200)        
        lots = response.json()['data']['lots']
        self.assertEqual(len(lots), 3)
        # update lots that do not have a dae
        for i, lot in enumerate(lots):
            if lot['dae'] == '':
                postdata = {
                    'tx_id': lot['id'],
                    'production_site': self.production_site.name,
                    'biocarburant_code': 'ETH',
                    'matiere_premiere_code': 'BLE',
                    'volume': 15000,
                    'pays_origine_code': 'FR',
                    'ep': 5,
                    'etd': 12,
                    'dae': 'DAEUPDATED%d' % (i),
                    'delivery_date': '2020-12-31',
                    'client': self.test_operator.name,
                    'delivery_site': '001',
                    'entity_id': self.test_producer.id,
                }
                response = self.client.post(reverse('api-v3-update-lot'), postdata)
                self.assertEqual(response.status_code, 200)        
        # get drafts, make sure we still have 3
        response = self.client.get(reverse('api-v3-lots-get'), {'entity_id': self.test_producer.id, 'status': 'draft', 'year': '2020'})
        self.assertEqual(response.status_code, 200)        
        lots = response.json()['data']['lots']
        self.assertEqual(len(lots), 3)
        # validate first lot
        response = self.client.post(reverse('api-v3-validate-lot'), {'entity_id': self.test_producer.id, 'tx_ids': [tx.id]})
        self.assertEqual(response.status_code, 200)
        res = response.json()
        self.assertEqual(res['submitted'], 1)
        self.assertEqual(res['valid'], 1)
        self.assertEqual(res['invalid'], 0)
        # check that we have only two drafts remaining
        response = self.client.get(reverse('api-v3-lots-get'), {'entity_id': self.test_producer.id, 'status': 'draft', 'year': '2020'})
        self.assertEqual(response.status_code, 200)        
        lots = response.json()['data']['lots']
        self.assertEqual(len(lots), 2)
        # validate-all the rest
        response = self.client.post(reverse('api-v3-validate-all-drafts'), {'entity_id': self.test_producer.id, 'year': '2020'})
        self.assertEqual(response.status_code, 200)
        res = response.json()
        self.assertEqual(res['submitted'], 2)
        self.assertEqual(res['valid'], 2)
        self.assertEqual(res['invalid'], 0)
        # get drafts, make sure we have 0 - all sent
        response = self.client.get(reverse('api-v3-lots-get'), {'entity_id': self.test_producer.id, 'status': 'draft', 'year': '2020'})
        self.assertEqual(response.status_code, 200)        
        data = response.json()['data']
        lots = data['lots']
        self.assertEqual(len(lots), 0)

        # as operator
        # make sure we received 3
        response = self.client.get(reverse('api-v3-lots-get'), {'entity_id': self.test_operator.id, 'status': 'in', 'year': '2020'})
        self.assertEqual(response.status_code, 200)        
        lots = response.json()['data']['lots']
        self.assertEqual(len(lots), 3)    
        # reject first
        tx_id1 = lots[0]['id']
        response = self.client.post(reverse('api-v3-reject-lot'), {'entity_id': self.test_operator.id, 'tx_ids': [tx_id1], 'comment': 'auto-reject-test'})
        self.assertEqual(response.status_code, 200)        
        # accept-with-reserves second + add comment
        tx_id2 = lots[1]['id']
        response = self.client.post(reverse('api-v3-accept-lot-with-reserves'), {'entity_id': self.test_operator.id, 'tx_ids': [tx_id2]})
        self.assertEqual(response.status_code, 200)        
        # accept third
        tx_id3 = lots[2]['id']
        response = self.client.post(reverse('api-v3-accept-lot'), {'entity_id': self.test_operator.id, 'tx_ids': [tx_id3]})
        self.assertEqual(response.status_code, 200)


    def test_advanced_template_import_cannot_validate(self):
        # as producer
        # upload lines that cannot be validated
        jsoned = self.upload_file('carbure_template_advanced_missing_data_cannot_validate.xlsx', self.test_producer)
        # get number of lots in excel file
        nb_lots = jsoned['data']['total']
        # make sure all lines were loaded
        self.assertEqual(nb_lots, jsoned['data']['loaded'])
        # make sure they were saved successfully
        self.ensure_nb_lots(nb_lots)
        self.ensure_nb_txs(nb_lots)

        # validate-all
        response = self.client.post(reverse('api-v3-validate-all-drafts'), {'entity_id': self.test_producer.id})
        self.assertEqual(response.status_code, 200)

        # get drafts
        lots = LotV2.objects.filter(added_by_user=self.user1, status='Draft')
        self.assertEqual(lots.count(), nb_lots) # they are still all with status draft

        # get drafts via api - same result expected
        response = self.client.get(reverse('api-v3-lots-get'), {'entity_id': self.test_producer.id, 'status': 'draft', 'year': '2020'})
        self.assertEqual(response.status_code, 200)        
        data = response.json()['data']
        lots = data['lots']
        self.assertEqual(len(lots), nb_lots)

        # make sure they all have LotError or TransactionError
        lot_errors = LotV2Error.objects.filter(lot__in=[lot['lot']['id'] for lot in lots])
        tx_errors = TransactionError.objects.filter(tx__in=[tx['id'] for tx in lots])
        nb_errors = lot_errors.count() + tx_errors.count()
        self.assertEqual(nb_errors, nb_lots)
        
        # delete-all-drafts
        response = self.client.post(reverse('api-v3-delete-all-drafts'), {'entity_id': self.test_producer.id, 'year': '2020'})
        self.assertEqual(response.status_code, 200)
        res = response.json()
        self.assertEqual(res['deleted'], nb_lots)

        # make sure no lots/tx/loterror/txerror are still there
        self.ensure_nb_lots(0)
        self.ensure_nb_txs(0)
        self.ensure_nb_lot_errors(0)
        self.ensure_nb_tx_errors(0)
        self.ensure_nb_sanity_errors(0)


    def test_advanced_template_import_can_validate(self):
        # upload valid lots
        jsoned = self.upload_file('carbure_template_advanced_missing_data_but_valid.xlsx', self.test_producer)
        nb_lots = jsoned['data']['total']
        self.assertEqual(jsoned['data']['loaded'], nb_lots)
        # validate-all
        response = self.client.post(reverse('api-v3-validate-all-drafts'), {'entity_id': self.test_producer.id, 'year': '2020'})
        self.assertEqual(response.status_code, 200)
        res = response.json()
        # make sure no lots/tx/loterror/txerror are still there
        self.assertEqual(res['submitted'], nb_lots)
        self.assertEqual(res['valid'], nb_lots)
        self.assertEqual(LotV2.objects.all().count(), nb_lots)
        self.assertEqual(LotTransaction.objects.all().count(), nb_lots)
        # get drafts 0
        lots = LotV2.objects.filter(added_by_user=self.user1, status='Draft')
        self.assertEqual(lots.count(), 0) # no more drafts, all validated
        # check api
        response = self.client.get(reverse('api-v3-lots-get'), {'entity_id': self.test_producer.id, 'status': 'draft', 'year': '2020'})
        self.assertEqual(response.status_code, 200)        
        data = response.json()['data']
        lots = data['lots']
        self.assertEqual(len(lots), 0)        
        # get validated nb_lots
        lots = LotV2.objects.filter(added_by_user=self.user1, status='Validated')
        self.assertEqual(lots.count(), nb_lots)
        lots = LotV2.objects.all()
        self.assertEqual(lots.count(), nb_lots)
        txs = LotTransaction.objects.all()
        self.assertEqual(txs.count(), nb_lots)

        # check api
        response = self.client.get(reverse('api-v3-lots-get'), {'entity_id': self.test_producer.id, 'status': 'validated', 'year': '2020'})
        self.assertEqual(response.status_code, 200)        
        lots = response.json()['data']['lots']
        self.assertEqual(len(lots), 0) # client is not in carbure, transactions are accepted automatically

        response = self.client.get(reverse('api-v3-lots-get'), {'entity_id': self.test_producer.id, 'status': 'accepted', 'year': '2020'})
        self.assertEqual(response.status_code, 200)        
        data = response.json()['data']
        lots = data['lots']
        all_lots = LotV2.objects.all().count()
        print('all lots count: %d' % (all_lots))
        self.assertEqual(len(lots), nb_lots)


    def test_template_import_can_validate(self):
        # upload valid lots
        jsoned = self.upload_file('carbure_template_simple_missing_data_but_valid.xlsx', self.test_producer)
        nb_lots = jsoned['data']['total']
        self.assertEqual(jsoned['data']['loaded'], nb_lots)
        print('uploaded %d lots' % (nb_lots))
        # validate-all
        response = self.client.post(reverse('api-v3-validate-all-drafts'), {'entity_id': self.test_producer.id, 'year': '2020'})
        self.assertEqual(response.status_code, 200)
        res = response.json()
        lots_in_batch = nb_lots - 1
        self.assertEqual(res['submitted'], lots_in_batch)
        self.assertEqual(res['valid'], lots_in_batch)

        # get drafts
        lots = LotV2.objects.filter(added_by_user=self.user1, status='Draft')
        self.assertEqual(lots.count(), 1) # one draft left (line without delivery_date)
        # check api
        response = self.client.get(reverse('api-v3-lots-get'), {'entity_id': self.test_producer.id, 'status': 'draft', 'year': '2020'})
        self.assertEqual(response.status_code, 200)        
        data = response.json()['data']
        lots = data['lots']
        self.assertEqual(len(lots), 0)
        # get validated nb_lots
        lots = LotV2.objects.filter(added_by_user=self.user1, status='Validated')
        self.assertEqual(lots.count(), lots_in_batch)
        lots = LotV2.objects.all()
        self.assertEqual(lots.count(), nb_lots)
        txs = LotTransaction.objects.all()
        self.assertEqual(txs.count(), nb_lots)

        # check api
        response = self.client.get(reverse('api-v3-lots-get'), {'entity_id': self.test_producer.id, 'status': 'validated', 'year': '2020'})
        self.assertEqual(response.status_code, 200)        
        lots = response.json()['data']['lots']
        self.assertEqual(len(lots), 0) # client is not in carbure, transactions are accepted automatically

        response = self.client.get(reverse('api-v3-lots-get'), {'entity_id': self.test_producer.id, 'status': 'accepted', 'year': '2020'})
        self.assertEqual(response.status_code, 200)        
        data = response.json()['data']
        lots = data['lots']
        self.assertEqual(len(lots), lots_in_batch)

    def test_simple_template_import_cannot_validate(self):
        # as producer
        # upload lines that cannot be validated
        jsoned = self.upload_file('carbure_template_simple_missing_data_cannot_validate.xlsx', self.test_producer)
        # get number of lots in excel file
        nb_lots = jsoned['data']['total']
        # make sure all lines were loaded
        self.assertEqual(nb_lots, jsoned['data']['loaded'])
        # make sure they were saved successfully
        lots = LotV2.objects.filter(added_by_user=self.user1)
        self.assertEqual(lots.count(), nb_lots)
        txs = LotTransaction.objects.filter(lot__in=lots)
        self.assertEqual(txs.count(), nb_lots)
        # validate-all
        response = self.client.post(reverse('api-v3-validate-all-drafts'), {'entity_id': self.test_producer.id})
        self.assertEqual(response.status_code, 200)
        # get drafts
        lots = LotV2.objects.filter(added_by_user=self.user1, status='Draft')
        self.assertEqual(lots.count(), nb_lots) # they are still all with status draft
        # get drafts via api - same result expected
        response = self.client.get(reverse('api-v3-lots-get'), {'entity_id': self.test_producer.id, 'status': 'draft', 'year': '2020'})
        self.assertEqual(response.status_code, 200)        
        data = response.json()['data']
        lots = data['lots']
        self.assertEqual(len(lots), nb_lots)
        # make sure they all have LotError or TransactionError

        lot_errors = [error.lot.id for error  in LotV2Error.objects.filter(lot__in=[lot['lot']['id'] for lot in lots])]
        tx_errors = [error.tx.lot.id for error in TransactionError.objects.filter(tx__in=[tx['id'] for tx in lots])]
        for lot in lots:
            self.assertTrue(lot['id'] in lot_errors or lot['id'] in tx_errors)
        
        # delete-all-drafts
        response = self.client.post(reverse('api-v3-delete-all-drafts'), {'entity_id': self.test_producer.id, 'year': '2020'})
        self.assertEqual(response.status_code, 200)
        res = response.json()
        self.assertEqual(res['deleted'], nb_lots)

        self.assertEqual(LotV2.objects.all().count(), 0)
        self.assertEqual(LotTransaction.objects.all().count(), 0)
        self.assertEqual(LotV2Error.objects.all().count(), 0)
        self.assertEqual(TransactionError.objects.all().count(), 0)

    def test_simple_template_import_sanity_checks(self):
        # as producer
        # upload lines that cannot be validated
        jsoned = self.upload_file('carbure_template_simple_wrong_data_cannot_validate.xlsx', self.test_producer)
        # get number of lots in excel file
        nb_lots = jsoned['data']['total']
        # make sure all lines were loaded
        self.assertEqual(nb_lots, jsoned['data']['loaded'])
        # make sure they were saved successfully
        lots = LotV2.objects.filter(added_by_user=self.user1)
        self.assertEqual(lots.count(), nb_lots)
        txs = LotTransaction.objects.filter(lot__in=lots)
        self.assertEqual(txs.count(), nb_lots)
        # validate-all
        debug_lots()

        response = self.client.post(reverse('api-v3-validate-all-drafts'), {'entity_id': self.test_producer.id, 'year': '2020'})
        self.assertEqual(response.status_code, 200)

        nb_invalid_dates = 3
        nb_okayish_lots = nb_lots - nb_invalid_dates
        # expect (nb_lots - nb_invalid_dates) submitted and 0 valid (2 lots have a stupid date)
        j = response.json()
        self.assertEqual(j['submitted'], nb_okayish_lots)
        self.assertEqual(j['valid'], 0)

        # get drafts
        lots = LotV2.objects.filter(added_by_user=self.user1, status='Draft')
        self.assertEqual(lots.count(), nb_lots) # they are still all with status draft
        # get drafts via api - same result expected
        response = self.client.get(reverse('api-v3-lots-get'), {'entity_id': self.test_producer.id, 'status': 'draft', 'year': '2020'})
        self.assertEqual(response.status_code, 200)        
        data = response.json()['data']
        lots = data['lots']
        self.assertEqual(len(lots), nb_okayish_lots)

        # make sure they all have an error
        lot_errors = [error.lot.id for error  in LotV2Error.objects.filter(lot__in=[lot['lot']['id'] for lot in lots])]
        tx_errors = [error.tx.lot.id for error in TransactionError.objects.filter(tx__in=[tx['id'] for tx in lots])]
        for lot in lots:
            self.assertTrue(lot['id'] in lot_errors or lot['id'] in tx_errors)
        
        # delete-all-drafts
        response = self.client.post(reverse('api-v3-delete-all-drafts'), {'entity_id': self.test_producer.id, 'year': '2020'})
        self.assertEqual(response.status_code, 200)
        res = response.json()
        self.assertEqual(res['deleted'], nb_okayish_lots)

    def test_duplicates(self):
        pass
        # as producer
        # create lot
        # validate
        # create same lot
        # validate again
        # ensure lot was deleted
        # as operator
        # create same lot
        # validate
        # lot doesn't exist anymore

        
        # as operator
        # create lot
        # validate
        # create same lot
        # validate again
        # ensure lot was deleted


        # as producer
        # create same lot
        # validate
        # validate returns "1 duplicate found"
        # lot is deleted but transaction using existing lot is created


    def test_real_behaviour(self):
        # download template without setting up parameters
        # download template after setup
        # upload simple template
        # upload advanced template
        # upload 10k lines
        # validate-all
        # upload 10k lines
        # delete-all
        # upload 100k lines
        # validate-all

        pass