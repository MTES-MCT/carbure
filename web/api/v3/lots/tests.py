import datetime
import os
import random
import time
import json
from django.test import TestCase
from django.test import TransactionTestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from core.models import Entity, UserRights, LotV2, LotTransaction, ProductionSite, Pays, Biocarburant, MatierePremiere, Depot, GenericError
from certificates.models import ISCCCertificate, EntityISCCTradingCertificate, DoubleCountingRegistration
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


def debug_errors(is_blocking=False):
    errors = GenericError.objects.all()
    if is_blocking:
        errors = errors.filter(is_blocking=True)
    for error in errors:
        print(error.natural_key())         

def get_random_dae():
    today = datetime.date.today()
    return 'TEST%dFR0000%d' % (today.year, random.randint(100000, 900000))


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
        UserRights.objects.update_or_create(user=self.user1, entity=self.test_producer, role='RW')
        UserRights.objects.update_or_create(user=self.user1, entity=self.test_operator, role='RW')
        UserRights.objects.update_or_create(user=self.user1, entity=self.entity3, role='RW')
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

    def ensure_nb_errors(self, nb):
        count = GenericError.objects.all().count()
        self.assertEqual(count, nb)

    def test_lot_actions(self):
        # as producer / trader
        dae = 'TEST2020FR00923-094-32094'
        lot = {
            'production_site': self.production_site.name,
            'production_site_commissioning_date': '01/12/2002',
            'production_site_reference': 'PRODSITEREFERENCE',
            'supplier_certificate': 'PRODSITEREFERENCE',
            'double_counting_registration': 'NUMDOUBLECOMPTE',
            'biocarburant_code': 'ETH',
            'matiere_premiere_code': 'BLE',
            'volume': 15000,
            'pays_origine_code': 'FR',
            'eec': 1.5,
            'ep': 5,
            'etd': 12,
            'dae': dae,
            'delivery_date': '2020-12-31',
            'client': self.test_operator.name,
            'delivery_site': '1',
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
        #print(data['transaction']['lot'])
        # make sure all data is correct
        self.assertEqual(data['transaction']['lot']['ep'], 6)
        self.assertEqual(data['transaction']['lot']['eec'], 1.5)
        self.assertEqual(data['transaction']['lot']['volume'], 15000)
        self.assertEqual(data['transaction']['lot']['pays_origine']['code_pays'], 'FR')
        self.assertEqual(data['transaction']['lot']['etd'], 12)
        self.assertEqual(data['transaction']['lot']['carbure_production_site_reference'], 'PRODSITEREFERENCE')
        self.assertEqual(data['transaction']['lot']['unknown_production_site_com_date'], '2002-12-01')
        self.assertEqual(data['transaction']['lot']['unknown_production_site_dbl_counting'], 'NUMDOUBLECOMPTE')

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
                    'eec': 1,
                    'ep': 5,
                    'etd': 12,
                    'dae': 'DAEUPDATED%d' % (i),
                    'delivery_date': '2020-12-31',
                    'client': self.test_operator.name,
                    'delivery_site': '01',
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
        res = response.json()['data']
        self.assertEqual(res['submitted'], 1)
        self.assertEqual(res['valid'], 1)
        self.assertEqual(res['invalid'], 0)
        # check that we have only two drafts remaining
        response = self.client.get(reverse('api-v3-lots-get'), {'entity_id': self.test_producer.id, 'status': 'draft', 'year': '2020'})
        self.assertEqual(response.status_code, 200)        
        lots = response.json()['data']['lots']
        self.assertEqual(len(lots), 2)
        # validate-all the rest
        txs = LotTransaction.objects.filter(lot__status='Draft')
        response = self.client.post(reverse('api-v3-validate-lot'), {'entity_id': self.test_producer.id, 'tx_ids': [tx.id for tx in txs]})
        self.assertEqual(response.status_code, 200)
        res = response.json()['data']
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
        txs = LotTransaction.objects.filter(lot__status='Draft')
        response = self.client.post(reverse('api-v3-validate-lot'), {'entity_id': self.test_producer.id, 'tx_ids': [tx.id for tx in txs]})
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

        # make sure they all have a GenericError
        errors = GenericError.objects.filter(tx__in=[tx['id'] for tx in lots])
        self.assertEqual(errors.count(), nb_lots)
        
        # delete-all-drafts
        txs = LotTransaction.objects.filter(lot__status='Draft')
        response = self.client.post(reverse('api-v3-delete-lot'), {'entity_id': self.test_producer.id, 'tx_ids': [tx.id for tx in txs]})      
        self.assertEqual(response.status_code, 200)
        res = response.json()
        self.assertEqual(res['deleted'], nb_lots)

        # make sure no lots/tx/loterror/txerror are still there
        self.ensure_nb_lots(0)
        self.ensure_nb_txs(0)
        self.ensure_nb_errors(0)


    def test_advanced_template_import_can_validate(self):
        # upload valid lots
        jsoned = self.upload_file('carbure_template_advanced_missing_data_but_valid.xlsx', self.test_producer)
        nb_lots = jsoned['data']['total']
        self.assertEqual(jsoned['data']['loaded'], nb_lots)
        # validate-all
        txs = LotTransaction.objects.filter(lot__status='Draft')
        response = self.client.post(reverse('api-v3-validate-lot'), {'entity_id': self.test_producer.id, 'tx_ids': [tx.id for tx in txs]})        
        self.assertEqual(response.status_code, 200)
        res = response.json()['data']
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
        self.assertEqual(len(lots), nb_lots)


    def test_template_import_can_validate(self):
        # upload valid lots
        jsoned = self.upload_file('carbure_template_simple_missing_data_but_valid.xlsx', self.test_producer)
        nb_lots = jsoned['data']['total']
        self.assertEqual(jsoned['data']['loaded'], nb_lots)
        # validate all 2020 lots (6). two wrong dates set to current year, everything else in 2020
        lots_2020 = nb_lots - 2
        txs = LotTransaction.objects.filter(lot__status='Draft', lot__period__startswith='2020')
        response = self.client.post(reverse('api-v3-validate-lot'), {'entity_id': self.test_producer.id, 'tx_ids': [tx.id for tx in txs]})          
        self.assertEqual(response.status_code, 200)
        res = response.json()['data']
        self.assertEqual(res['submitted'], lots_2020)
        self.assertEqual(res['valid'], lots_2020)

        # get drafts
        txs = LotTransaction.objects.filter(lot__added_by_user=self.user1, lot__status='Draft')
        self.assertEqual(txs.count(), 2) # two drafts left (line without delivery_date and line with far away date)

        # validate them manually
        response = self.client.post(reverse('api-v3-validate-lot'), {'entity_id': self.test_producer.id, 'tx_ids': [tx.id for tx in txs]})          
        self.assertEqual(response.status_code, 200)

        # check api
        response = self.client.get(reverse('api-v3-lots-get'), {'entity_id': self.test_producer.id, 'status': 'draft', 'year': '2020'})
        self.assertEqual(response.status_code, 200)        
        data = response.json()['data']
        lots = data['lots']
        self.assertEqual(len(lots), 0)

        tx = LotTransaction.objects.filter(lot__added_by_user=self.user1, lot__status='Draft')
        self.assertEqual(tx.count(), 0) # no more drafts, everything has been validated

        # check api
        response = self.client.get(reverse('api-v3-lots-get'), {'entity_id': self.test_producer.id, 'status': 'validated', 'year': '2020'})
        self.assertEqual(response.status_code, 200)        
        lots = response.json()['data']['lots']
        self.assertEqual(len(lots), lots_2020 - 1) # 1 tx has an empty client (producer himself - automatically accepted). For other, client is in carbure so transactions are pending acceptation
        response = self.client.get(reverse('api-v3-lots-get'), {'entity_id': self.test_producer.id, 'status': 'accepted', 'year': '2020'})
        self.assertEqual(response.status_code, 200)
        data = response.json()['data']
        lots = data['lots']
        self.assertEqual(len(lots), 1)

    def test_simple_template_import_missing_data_cannot_validate(self):
        # as producer
        # upload lines that cannot be validated
        jsoned = self.upload_file('carbure_template_simple_missing_data_cannot_validate.xlsx', self.test_producer)
        # get number of lots in excel file
        total_lots = jsoned['data']['total']
        nb_lots = jsoned['data']['loaded']
        # make sure all lines were loaded minus the one missing biocarburant_code
        self.assertEqual(nb_lots, total_lots - 1)
        # make sure they were saved successfully
        lots = LotV2.objects.filter(added_by_user=self.user1)
        self.assertEqual(lots.count(), nb_lots)
        txs = LotTransaction.objects.filter(lot__in=lots)
        self.assertEqual(txs.count(), nb_lots)
        # validate-all
        txs = LotTransaction.objects.filter(lot__status='Draft')
        response = self.client.post(reverse('api-v3-validate-lot'), {'entity_id': self.test_producer.id, 'tx_ids': [tx.id for tx in txs]})      
        self.assertEqual(response.status_code, 200)
        # get drafts
        lots = LotV2.objects.filter(added_by_user=self.user1, status='Draft')
        debug_transactions()
        self.assertEqual(lots.count(), nb_lots) # they are still all with status draft
        # get drafts via api - same result expected
        response = self.client.get(reverse('api-v3-lots-get'), {'entity_id': self.test_producer.id, 'status': 'draft', 'year': '2020'})
        self.assertEqual(response.status_code, 200)        
        data = response.json()['data']
        lots = data['lots']
        self.assertEqual(len(lots), nb_lots)
        # make sure they all have a GenericError
        for lot in lots:
            errors = GenericError.objects.filter(tx=lot['id']).count()
            self.assertGreater(errors, 0)

        # delete-all-drafts
        txs = LotTransaction.objects.filter(lot__status='Draft')
        response = self.client.post(reverse('api-v3-delete-lot'), {'entity_id': self.test_producer.id, 'tx_ids': [tx.id for tx in txs]})    
        self.assertEqual(response.status_code, 200)
        res = response.json()
        self.assertEqual(res['deleted'], nb_lots)

        self.assertEqual(LotV2.objects.all().count(), 0)
        self.assertEqual(LotTransaction.objects.all().count(), 0)
        self.assertEqual(GenericError.objects.all().count(), 0)


    def test_simple_template_import_cannot_validate(self):
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
        txs = LotTransaction.objects.filter(lot__status='Draft')
        response = self.client.post(reverse('api-v3-validate-lot'), {'entity_id': self.test_producer.id, 'tx_ids': [tx.id for tx in txs]})              
        self.assertEqual(response.status_code, 200)
        # expect (nb_lots - nb_invalid_dates) submitted and 0 valid (2 lots have a stupid date)
        j = response.json()['data']
        self.assertEqual(j['submitted'], nb_lots)
        self.assertEqual(j['valid'], 0)


        # get drafts
        lots = LotV2.objects.filter(added_by_user=self.user1, status='Draft')
        self.assertEqual(lots.count(), nb_lots) # they are still all with status draft
        # get drafts via api - same result expected
        response = self.client.get(reverse('api-v3-lots-get'), {'entity_id': self.test_producer.id, 'status': 'draft', 'year': '2020'})
        self.assertEqual(response.status_code, 200)        
        data = response.json()['data']
        lots = data['lots']
        self.assertEqual(len(lots), nb_lots - 2) # 3 lots have a stupid date that won't be counted in 2020

        # make sure they all have an error
        for lot in lots:
            errors = GenericError.objects.filter(tx=lot['id']).count()
            self.assertGreater(errors, 0)
        
        # delete-all-drafts
        txs = LotTransaction.objects.filter(lot__status='Draft')
        response = self.client.post(reverse('api-v3-delete-lot'), {'entity_id': self.test_producer.id, 'tx_ids': [tx.id for tx in txs]})    
        self.assertEqual(response.status_code, 200)
        res = response.json()
        self.assertEqual(res['deleted'], nb_lots)

    def test_duplicates_producer(self):
        # cleanup db
        LotTransaction.objects.all().delete()
        LotV2.objects.all().delete()
        # as producer, create lot
        dae = 'TEST2020FR00923-DUP-32094'
        lot = {
            'production_site': self.production_site.name,
            'biocarburant_code': 'ETH',
            'matiere_premiere_code': 'BLE',
            'volume': 15000,
            'pays_origine_code': 'FR',
            'supplier_certificate': 'ISCC-TOTO-02',
            'eec': 1,
            'ep': 5,
            'etd': 12,
            'dae': dae,
            'delivery_date': '2020-12-31',
            'client': self.test_operator.name,
            'delivery_site': '001',
            'entity_id': self.test_producer.id,
        }
        response = self.client.post(reverse('api-v3-add-lot'), lot)
        self.assertEqual(response.status_code, 200)  
        # validate
        tx = LotTransaction.objects.get(dae=dae)
        response = self.client.post(reverse('api-v3-validate-lot'), {'tx_ids': [tx.id], 'entity_id': self.test_producer.id})
        self.assertEqual(response.status_code, 200)

        # create same lot
        response = self.client.post(reverse('api-v3-add-lot'), lot)
        self.assertEqual(response.status_code, 200)
        # validate again
        tx = LotTransaction.objects.get(dae=dae, lot__status='Draft')
        response = self.client.post(reverse('api-v3-validate-lot'), {'tx_ids': [tx.id], 'entity_id': self.test_producer.id})
        self.assertEqual(response.status_code, 200)
        j = response.json()['data']
        self.assertEqual(j['duplicates'], 1)
        # ensure lot was deleted
        nb_lots = LotV2.objects.all().count()
        self.assertEqual(nb_lots, 1)
        # as operator, create same lot
        lot['production_site'] = ''
        lot['supplier_certificate'] = 'ISCC-TOTO-02'
        lot['production_site_commissioning_date'] = '11/12/1998'
        lot['producer_name'] = self.test_producer.name
        lot['entity_id'] = self.test_operator.id

        response = self.client.post(reverse('api-v3-add-lot'), lot)
        self.assertEqual(response.status_code, 200)
        j = response.json()['data']
        # validate
        tx = LotTransaction.objects.get(dae=dae, lot__added_by=self.test_operator)
        response = self.client.post(reverse('api-v3-validate-lot'), {'tx_ids': [tx.id], 'entity_id': self.test_operator.id})
        self.assertEqual(response.status_code, 200)
        # lot doesn't exist anymore
        cnt = LotTransaction.objects.filter(dae=dae, lot__added_by=self.test_operator).count()
        self.assertEqual(cnt, 0)

    def test_dates_format(self):
        # cleanup db
        LotTransaction.objects.all().delete()
        LotV2.objects.all().delete()
        # as producer, create lot
        dae = 'TEST2020FR00923-DUP-32094'
        lot = {
            'production_site': "unknown production site",
            'production_site_commissioning_date': '2001-12-01',
            'biocarburant_code': 'ETH',
            'matiere_premiere_code': 'BLE',
            'volume': 15000,
            'pays_origine_code': 'FR',
            'eec': 1,
            'ep': 5,
            'etd': 12,
            'dae': dae,
            'delivery_date': '2020-12-01',
            'client': self.test_operator.name,
            'delivery_site': '001',
            'entity_id': self.test_producer.id,
        }
        response = self.client.post(reverse('api-v3-add-lot'), lot)
        self.assertEqual(response.status_code, 200)  
        # check
        tx = LotTransaction.objects.get(dae=dae)
        dt1 = datetime.date(2001, 12, 1)
        dt2 = datetime.date(2020, 12, 1)
        self.assertEqual(tx.lot.unknown_production_site_com_date, dt1)
        self.assertEqual(tx.delivery_date, dt2)

        LotTransaction.objects.all().delete()
        LotV2.objects.all().delete()
        # as producer, create lot
        dae = 'TEST2020FR00923-DUP-32094'
        lot = {
            'production_site': "unknown production site",
            'production_site_commissioning_date': '01/12/2001',
            'biocarburant_code': 'ETH',
            'matiere_premiere_code': 'BLE',
            'volume': 15000,
            'pays_origine_code': 'FR',
            'eec': 1,
            'ep': 5,
            'etd': 12,
            'dae': dae,
            'delivery_date': '01/12/2020',
            'client': self.test_operator.name,
            'delivery_site': '001',
            'entity_id': self.test_producer.id,
        }
        response = self.client.post(reverse('api-v3-add-lot'), lot)
        self.assertEqual(response.status_code, 200)  
        # check
        tx = LotTransaction.objects.get(dae=dae)
        dt1 = datetime.date(2001, 12, 1)
        dt2 = datetime.date(2020, 12, 1)
        self.assertEqual(tx.lot.unknown_production_site_com_date, dt1)
        self.assertEqual(tx.delivery_date, dt2)

    def test_duplicates_operator(self):
        # cleanup db
        LotTransaction.objects.all().delete()
        LotV2.objects.all().delete()
        # as operator, create lot
        dae = 'TEST2020FR00923-DUP-32094'
        lot = {
            'supplier_certificate': 'ISCC-TOTO-02',
            'production_site_commissioning_date': '11/12/1998',
            'biocarburant_code': 'ETH',
            'matiere_premiere_code': 'BLE',
            'volume': 15000,
            'pays_origine_code': 'FR',
            'eec': 1,
            'ep': 5,
            'etd': 12,
            'dae': dae,
            'delivery_date': '2020-12-31',
            'client': self.test_operator.name,
            'delivery_site': '001',
            'entity_id': self.test_operator.id,
        }
        response = self.client.post(reverse('api-v3-add-lot'), lot)
        self.assertEqual(response.status_code, 200)  
        # validate
        tx = LotTransaction.objects.get(dae=dae)
        response = self.client.post(reverse('api-v3-validate-lot'), {'tx_ids': [tx.id], 'entity_id': self.test_operator.id})
        self.assertEqual(response.status_code, 200)
        drafts = LotTransaction.objects.filter(dae=dae, lot__status='Draft').count()
        valid = LotTransaction.objects.filter(dae=dae, lot__status='Validated').count()
        self.assertEqual(drafts, 0)
        self.assertEqual(valid, 1)


        # create same lot
        response = self.client.post(reverse('api-v3-add-lot'), lot)
        self.assertEqual(response.status_code, 200)
        # validate again
        tx = LotTransaction.objects.get(dae=dae, lot__status='Draft')
        response = self.client.post(reverse('api-v3-validate-lot'), {'tx_ids': [tx.id], 'entity_id': self.test_operator.id})
        self.assertEqual(response.status_code, 200)
        j = response.json()['data']
        self.assertEqual(j['duplicates'], 1)
        # ensure lot was deleted
        nb_lots = LotV2.objects.all().count()
        self.assertEqual(nb_lots, 1)

        # as producer, create same lot
        lot['entity_id'] = self.test_producer.id
        del lot['production_site_commissioning_date']
        lot['production_site'] = self.production_site.name
        response = self.client.post(reverse('api-v3-add-lot'), lot)
        self.assertEqual(response.status_code, 200)
        # validate
        tx = LotTransaction.objects.get(dae=dae, lot__added_by=self.test_producer)
        response = self.client.post(reverse('api-v3-validate-lot'), {'tx_ids': [tx.id], 'entity_id': self.test_producer.id})
        self.assertEqual(response.status_code, 200)
        j = response.json()
        # lot has replaced the previous one
        nb_lots = LotV2.objects.all().count()
        self.assertEqual(nb_lots, 1)
        nb_tx = LotTransaction.objects.all().count()
        self.assertEqual(nb_tx, 1)
        tx = LotTransaction.objects.get(dae=dae)
        self.assertEqual(tx.lot.producer_is_in_carbure, True)
        self.assertEqual(tx.lot.carbure_producer.id, self.test_producer.id)
        self.assertEqual(tx.carbure_client.id, self.test_operator.id)
        self.assertEqual(tx.lot.carbure_production_site.id, self.production_site.id)
        self.assertEqual(tx.lot.production_site_is_in_carbure, True)




    def test_duplicates_upload(self):
        today = datetime.date.today()
        # add certificate to test_producer
        crt, created = ISCCCertificate.objects.update_or_create(certificate_id='ISCC-TOTO-02', certificate_holder='das super producteur test', addons='TRS', valid_from=today, valid_until=today)
        EntityISCCTradingCertificate.objects.update_or_create(entity=self.test_producer, certificate=crt)

        # upload excel file
        jsoned = self.upload_file('carbure_duplicates.xlsx', self.test_producer)
        # get number of lots in excel file
        nb_lots = jsoned['data']['total']
        # make sure all lines were loaded
        self.assertEqual(nb_lots, jsoned['data']['loaded'])
        
        # validate-all
        txs = LotTransaction.objects.filter(lot__status='Draft')
        response = self.client.post(reverse('api-v3-validate-lot'), {'entity_id': self.test_producer.id, 'tx_ids': [tx.id for tx in txs]})              
        self.assertEqual(response.status_code, 200)
        j = response.json()
        # duplicates > 0
        self.assertGreater(j['data']['duplicates'], 0)
        # no more drafts
        nb_drafts = LotV2.objects.filter(status='Draft').count()
        self.assertEqual(nb_drafts, 0)
        nb_lots = LotV2.objects.all().count()

        # upload same file again and validate
        jsoned = self.upload_file('carbure_duplicates.xlsx', self.test_producer)
        nb_lots_uploaded = jsoned['data']['loaded']

        txs = LotTransaction.objects.filter(lot__status='Draft')
        response = self.client.post(reverse('api-v3-validate-lot'), {'entity_id': self.test_producer.id, 'tx_ids': [tx.id for tx in txs]})  
        jsoned = response.json()
        self.assertEqual(jsoned['data']['duplicates'], nb_lots_uploaded)
        nb_drafts = LotV2.objects.filter(status='Draft').count()
        # all drafts have been considered as duplicates
        self.assertEqual(nb_drafts, 0)
        # no additional lot created
        total_lots = LotV2.objects.all().count()
        self.assertEqual(nb_lots, total_lots)


    def create_lot(self, **kwargs):
        producer = self.test_producer
        production_site = self.production_site
        lot = {
            'supplier_certificate': 'ISCC-TOTO-02',
            'biocarburant_code': 'ETH',
            'matiere_premiere_code': 'BLE',
            'producer': producer.name,
            'production_site': production_site.name,
            'volume': 15000,
            'pays_origine_code': 'FR',
            'eec': 1,
            'ep': 5,
            'etd': 12,
            'dae': get_random_dae(),
            'delivery_date': '2020-12-31',
            'client': self.test_operator.name,
            'delivery_site': '001',
            'entity_id': self.test_producer.id,
        }
        lot.update(kwargs)
        response = self.client.post(reverse('api-v3-add-lot'), lot)
        self.assertEqual(response.status_code, 200)
        data = response.json()['data']
        tx_id = data['id']
        lot_id = data['lot']['id']
        return tx_id, lot_id

  
    def test_production_site_strip(self):
        psitename = '   ' + self.production_site.name + '   '
        tx_id, lot_id = self.create_lot(production_site=psitename)
        lot = LotV2.objects.get(id=lot_id)
        self.assertEqual(lot.production_site_is_in_carbure, True)
        self.assertEqual(lot.carbure_production_site.name, self.production_site.name)


    def test_download_templates(self):
        response = self.client.get(reverse('api-v3-template-simple'), {'entity_id': self.test_producer.id})
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('api-v3-template-advanced'), {'entity_id': self.test_producer.id})
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('api-v3-template-blend'), {'entity_id': self.test_operator.id})
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('api-v3-template-trader'), {'entity_id': self.entity3.id})
        self.assertEqual(response.status_code, 200)


    def test_real_behaviour(self):
        # download simple template
        response = self.client.get(reverse('api-v3-template-simple'), {'entity_id': self.test_producer.id})
        self.assertEqual(response.status_code, 200)
        filecontent = response.content

        # upload simple template
        f = SimpleUploadedFile("template.xslx", filecontent)
        response = self.client.post(reverse('api-v3-upload'), {'entity_id': self.test_producer.id, 'file': f})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(LotV2.objects.all().count(), 10)
        self.assertEqual(LotTransaction.objects.all().count(), 10)

        # download advanced template
        response = self.client.get(reverse('api-v3-template-advanced'), {'entity_id': self.test_producer.id})
        self.assertEqual(response.status_code, 200)
        filecontent = response.content        
        # upload advanced template
        f = SimpleUploadedFile("templateadvanced.xslx", filecontent)
        response = self.client.post(reverse('api-v3-upload'), {'entity_id': self.test_producer.id, 'file': f})
        self.assertEqual(LotV2.objects.all().count(), 20)
        self.assertEqual(LotTransaction.objects.all().count(), 20)


    def test_client_case_sensitiveness(self):
        # as producer / trader
        dae = 'TEST2020FR00923-094-32094'
        lot = {
            'production_site': self.production_site.name,
            'production_site_commissioning_date': '01/12/2002',
            'supplier_reference': 'PRODSITEREFERENCE',
            'double_counting_registration': 'NUMDOUBLECOMPTE',
            'biocarburant_code': 'ETH',
            'matiere_premiere_code': 'BLE',
            'volume': 15000,
            'pays_origine_code': 'FR',
            'eec': 1.5,
            'ep': 5,
            'etd': 12,
            'dae': dae,
            'delivery_date': '2020-12-31',
            'client': self.test_operator.name.lower(),
            'delivery_site': '1',
            'entity_id': self.test_producer.id,
        }
        # add manual lot
        response = self.client.post(reverse('api-v3-add-lot'), lot)
        self.assertEqual(response.status_code, 200)  
        tx = LotTransaction.objects.get(dae=dae)
        response = self.client.get(reverse('api-v3-lots-get-details'), {'entity_id': self.test_producer.id, 'tx_id': tx.id})
        self.assertEqual(response.status_code, 200)        
        data = response.json()['data']
        self.assertEqual(data['transaction']['client_is_in_carbure'], True)
        
    def test_double_count_certificates_expiration(self):
        # create 2 double count certificates. one valid, one expired
        today = datetime.date.today()
        vfrom = today - datetime.timedelta(days=365)
        vuntil = today
        DoubleCountingRegistration.objects.update_or_create(certificate_id="DC_CERT_01", certificate_holder="Super testeur", 
        defaults={'registered_address':"blablabla", 'valid_from': vfrom, 'valid_until': today})
        DoubleCountingRegistration.objects.update_or_create(certificate_id="DC_CERT_02", certificate_holder="Super testeur", 
        defaults={'registered_address':"blablabla", 'valid_from': vfrom, 'valid_until': vuntil - datetime.timedelta(days=7)})        
        # upload lot using first
        tx_id, lot_id = self.create_lot(matiere_premiere_code="RESIDUS_DE_BIERE", biocarburant_code="ETH", double_counting_registration="DC_CERT_01", delivery_date=today.strftime("%d/%m/%Y"))
        self.assertEqual(GenericError.objects.filter(error="UNKNOWN_DOUBLE_COUNTING_CERTIFICATE").count(), 0)
        self.assertEqual(GenericError.objects.filter(error="EXPIRED_DOUBLE_COUNTING_CERTIFICATE").count(), 0)
        # upload lot using second
        tx_id, lot_id = self.create_lot(matiere_premiere_code="RESIDUS_DE_BIERE", biocarburant_code="ETH", double_counting_registration="DC_CERT_02", delivery_date=today.strftime("%d/%m/%Y"))
        self.assertEqual(GenericError.objects.filter(error="UNKNOWN_DOUBLE_COUNTING_CERTIFICATE").count(), 0)
        self.assertEqual(GenericError.objects.filter(error="EXPIRED_DOUBLE_COUNTING_CERTIFICATE").count(), 1)
        # upload lot using unknown cert
        GenericError.objects.all().delete()
        tx_id, lot_id = self.create_lot(matiere_premiere_code="RESIDUS_DE_BIERE", biocarburant_code="ETH", double_counting_registration="UNKNOWN_DC_CERT")
        self.assertEqual(GenericError.objects.filter(error="UNKNOWN_DOUBLE_COUNTING_CERTIFICATE").count(), 1)
        self.assertEqual(GenericError.objects.filter(error="EXPIRED_DOUBLE_COUNTING_CERTIFICATE").count(), 0)

class DeclarationTests(TransactionTestCase):
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

        # some rights
        UserRights.objects.update_or_create(user=self.user1, entity=self.test_producer, role='RW')
        UserRights.objects.update_or_create(user=self.user1, entity=self.test_operator, role='RW')

        loggedin = self.client.login(username=self.user_email, password=self.user_password)
        self.assertTrue(loggedin)          
        # pass otp verification
        response = self.client.get(reverse('otp-verify'))
        self.assertEqual(response.status_code, 200)
        device = EmailDevice.objects.get(user=self.user1)
        response = self.client.post(reverse('otp-verify'), {'otp_token': device.token})
        self.assertEqual(response.status_code, 302)        

    def create_lot(self, **kwargs):
        producer = self.test_producer
        lot = {
            'supplier_certificate': 'ISCC-TOTO-02',
            'biocarburant_code': 'ETH',
            'matiere_premiere_code': 'BLE',
            'producer': producer.name,
            'production_site': "usine non repertoriee",
            'volume': 15000,
            'pays_origine_code': 'FR',
            'eec': 1,
            'ep': 5,
            'etd': 12,
            'dae': get_random_dae(),
            'delivery_date': '2020-12-31',
            'client': self.test_operator.name,
            'delivery_site': '001',
            'entity_id': self.test_producer.id,
        }
        lot.update(kwargs)
        response = self.client.post(reverse('api-v3-add-lot'), lot)
        self.assertEqual(response.status_code, 200)
        data = response.json()['data']
        tx_id = data['id']
        lot_id = data['lot']['id']
        return tx_id, lot_id


    def test_declare(self):
        today = datetime.date.today()
        # create lots for client
        tx_id, lot_id = self.create_lot(delivery_date=today.strftime('%Y-%m-%d'))
        # validate
        tx = LotTransaction.objects.get(id=tx_id)
        tx.delivery_status = LotTransaction.PENDING
        tx.save()
        tx.lot.status = LotV2.VALIDATED
        tx.lot.save()        
        # try validate declaration (doesnt work)
        response = self.client.post(reverse('api-v3-validate-declaration'), {'entity_id': self.test_producer.id, 'period_year': today.year, 'period_month': today.strftime('%m')})
        self.assertEqual(response.status_code, 400)
        jsoned = response.json()
        self.assertEqual(jsoned['message'], "PENDING_TRANSACTIONS_CANNOT_DECLARE")

        # as client, accept lots
        tx.delivery_status = LotTransaction.ACCEPTED
        tx.save()

        # try validate declaration (ok)
        response = self.client.post(reverse('api-v3-validate-declaration'), {'entity_id': self.test_producer.id, 'period_year': today.year, 'period_month': today.strftime('%m')})
        self.assertEqual(response.status_code, 200)
        tx = LotTransaction.objects.get(id=tx_id)
        self.assertEqual(tx.delivery_status, LotTransaction.FROZEN)


class CorrectionTests(TransactionTestCase):
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
        self.test_trader, _ = Entity.objects.update_or_create(name='Trader1', entity_type=Entity.TRADER)

        # some rights
        UserRights.objects.update_or_create(user=self.user1, entity=self.test_producer, defaults={'role': 'RW'})
        UserRights.objects.update_or_create(user=self.user1, entity=self.test_operator, defaults={'role': 'RW'})
        UserRights.objects.update_or_create(user=self.user1, entity=self.test_trader, defaults={'role': 'RW'})

        # a production site and delivery_site
        france = Pays.objects.get(code_pays='FR')
        Depot.objects.update_or_create(name='Depot Test', depot_id='001', country=france)
        Depot.objects.update_or_create(name='Depot Test 2', depot_id='002', country=france)
        today = datetime.date.today()
        d = {'country': france, 'date_mise_en_service': today, 'site_id':'SIRET XXX',
        'city': 'paris', 'postal_code': '75001', 'manager_name':'Guillaume Caillou', 
        'manager_phone':'0145247000', 'manager_email': 'test@test.net'}
        self.production_site, _ = ProductionSite.objects.update_or_create(producer=self.test_producer, name='PSITE1', defaults=d)        

        loggedin = self.client.login(username=self.user_email, password=self.user_password)
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
            'producer': self.test_producer.name,
            'production_site': "PSITE1",
            'volume': 15000,
            'pays_origine_code': 'FR',
            'eec': 1,
            'ep': 5,
            'etd': 12,
            'dae': get_random_dae(),
            'delivery_date': '2020-12-31',
            'client': self.test_trader.name,
            'delivery_site': '001',
            'entity_id': self.test_producer.id,
        }
        lot.update(kwargs)
        response = self.client.post(reverse('api-v3-add-lot'), lot)
        self.assertEqual(response.status_code, 200)
        data = response.json()['data']
        tx_id = data['id']
        lot_id = data['lot']['id']
        return tx_id, lot_id, lot

    def test_delivery_site_by_name(self):
        # 1 create lot as producer and send it
        tx_id, lot_id, j = self.create_lot(client=self.test_operator.name, delivery_site='depot test')
        tx = LotTransaction.objects.get(id=tx_id)
        self.assertEqual(tx.carbure_delivery_site.depot_id, '001')

        tx_id, lot_id, j = self.create_lot(client=self.test_operator.name, delivery_site='001')
        tx = LotTransaction.objects.get(id=tx_id)
        self.assertEqual(tx.carbure_delivery_site.depot_id, '001')


    def test_only_creator_can_validate(self):
        # 1 create lot as producer and send it
        tx_id, lot_id, j = self.create_lot(client=self.test_operator.name)
        # try validate as client
        response = self.client.post(reverse('api-v3-validate-lot'), {'entity_id': self.test_operator.id, 'tx_ids': [tx_id]})
        self.assertEqual(response.status_code, 403)              
        # try validate as unknown
        response = self.client.post(reverse('api-v3-validate-lot'), {'entity_id': self.test_trader.id, 'tx_ids': [tx_id]})
        self.assertEqual(response.status_code, 403)              
        # try validate as creator
        response = self.client.post(reverse('api-v3-validate-lot'), {'entity_id': self.test_producer.id, 'tx_ids': [tx_id]})
        self.assertEqual(response.status_code, 200)        

    def test_only_creator_can_validate__createdbyoperator(self):
        # 1 create lot as producer and send it
        tx_id, lot_id, j = self.create_lot(producer='unknownproducer', production_site_reference='psitereference', date_mise_en_service='12/12/2012', client=self.test_operator.name, entity_id=self.test_operator.id)
        # try validate as unknown
        response = self.client.post(reverse('api-v3-validate-lot'), {'entity_id': self.test_producer.id, 'tx_ids': [tx_id]})
        self.assertEqual(response.status_code, 403)              
        # try validate as client
        response = self.client.post(reverse('api-v3-validate-lot'), {'entity_id': self.test_operator.id, 'tx_ids': [tx_id]})
        self.assertEqual(response.status_code, 200)

    def test_only_client_can_accept(self):
        # 1 create lot as producer and send it
        tx_id, lot_id, j = self.create_lot(client=self.test_operator.name)
        response = self.client.post(reverse('api-v3-validate-lot'), {'entity_id': self.test_producer.id, 'tx_ids': [tx_id]})
        self.assertEqual(response.status_code, 200)        
        # 2 producer cannot accept
        response = self.client.post(reverse('api-v3-accept-lot'), {'entity_id': self.test_producer.id, 'tx_ids': [tx_id]})
        self.assertEqual(response.status_code, 403)
        # random cannot accept
        response = self.client.post(reverse('api-v3-accept-lot'), {'entity_id': self.test_trader.id, 'tx_ids': [tx_id]})
        self.assertEqual(response.status_code, 403)        
        # client can accept
        response = self.client.post(reverse('api-v3-accept-lot'), {'entity_id': self.test_operator.id, 'tx_ids': [tx_id]})
        self.assertEqual(response.status_code, 200)           

    def test_only_creator_can_update_lot__producer(self):
        # 1 producer creates lot
        tx_id, lot_id, j = self.create_lot()
        # update some data
        j['tx_id'] = tx_id
        j['volume'] = 45000
        j['delivery_date'] = '2021-01-15'
        j['entity_id'] = self.test_operator.id
        response = self.client.post(reverse('api-v3-update-lot'), j)
        self.assertEqual(response.status_code, 403)
        j['entity_id'] = self.test_trader.id
        response = self.client.post(reverse('api-v3-update-lot'), j)
        self.assertEqual(response.status_code, 403)
        j['entity_id'] = self.test_producer.id
        response = self.client.post(reverse('api-v3-update-lot'), j)
        self.assertEqual(response.status_code, 200)

    def test_only_creator_can_update_lot__trader(self):
        # 1 operator creates lot
        tx_id, lot_id, j = self.create_lot(producer='UNKNOWNPRODUCER', entity_id=self.test_trader.id)
        # update some data
        j['tx_id'] = tx_id
        j['volume'] = 45000
        j['delivery_date'] = '2021-01-15'
        j['entity_id'] = self.test_producer.id
        response = self.client.post(reverse('api-v3-update-lot'), j)
        self.assertEqual(response.status_code, 403)
        j['entity_id'] = self.test_trader.id
        response = self.client.post(reverse('api-v3-update-lot'), j)
        self.assertEqual(response.status_code, 200)
        j['entity_id'] = self.test_operator.id
        response = self.client.post(reverse('api-v3-update-lot'), j)
        self.assertEqual(response.status_code, 403)

    def test_only_creator_can_update_lot__operator(self):
        # 1 operator creates lot
        tx_id, lot_id, j = self.create_lot(producer='UNKNOWNPRODUCER', entity_id=self.test_operator.id)
        # update some data
        j['tx_id'] = tx_id
        j['volume'] = 45000
        j['delivery_date'] = '2021-01-15'
        j['entity_id'] = self.test_producer.id
        response = self.client.post(reverse('api-v3-update-lot'), j)
        self.assertEqual(response.status_code, 403)
        j['entity_id'] = self.test_trader.id
        response = self.client.post(reverse('api-v3-update-lot'), j)
        self.assertEqual(response.status_code, 403)
        j['entity_id'] = self.test_operator.id
        response = self.client.post(reverse('api-v3-update-lot'), j)
        self.assertEqual(response.status_code, 200)

    def test_only_client_can_request_correction(self):
        # 1 producer creates lot
        tx_id, lot_id, j = self.create_lot()
        # 2 validate
        response = self.client.post(reverse('api-v3-validate-lot'), {'entity_id': self.test_producer.id, 'tx_ids': [tx_id]})
        self.assertEqual(response.status_code, 200)

        # 3 request a correction
        # 3.1 the sender requests a correction - 403
        response = self.client.post(reverse('api-v3-accept-lot-with-reserves'), {'entity_id': self.test_producer.id, 'tx_ids': [tx_id]})
        self.assertEqual(response.status_code, 403)

        # 3.2 someone else requests a correction - 403
        response = self.client.post(reverse('api-v3-accept-lot-with-reserves'), {'entity_id': self.test_operator.id, 'tx_ids': [tx_id]})
        self.assertEqual(response.status_code, 403)

        # 3.3 the real client requests a correction - 200
        response = self.client.post(reverse('api-v3-accept-lot-with-reserves'), {'entity_id': self.test_trader.id, 'tx_ids': [tx_id]})
        self.assertEqual(response.status_code, 200)

    def test_only_creator_can_amend(self):
        # 1 producer creates lot
        tx_id, lot_id, j = self.create_lot()
        # 2 validate
        response = self.client.post(reverse('api-v3-validate-lot'), {'entity_id': self.test_producer.id, 'tx_ids': [tx_id]})
        self.assertEqual(response.status_code, 200)

        # 3 request to edit lot
        # 3.1 the sender requests to amend - 200
        response = self.client.post(reverse('api-v3-amend-lot'), {'entity_id': self.test_producer.id, 'tx_id': tx_id})
        self.assertEqual(response.status_code, 200)

        # 3.2 someone else requests to amend - 403
        response = self.client.post(reverse('api-v3-amend-lot'), {'entity_id': self.test_operator.id, 'tx_id': tx_id})
        self.assertEqual(response.status_code, 403)

        # 3.3 the client requests to amend - 403
        response = self.client.post(reverse('api-v3-amend-lot'), {'entity_id': self.test_trader.id, 'tx_id': tx_id})
        self.assertEqual(response.status_code, 403)


    def test_split_rights(self):
        # producer creates lot and validates
        tx_id, lot_id, j = self.create_lot()
        response = self.client.post(reverse('api-v3-validate-lot'), {'entity_id': self.test_producer.id, 'tx_ids': [tx_id]})
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('api-v3-amend-lot'), {'entity_id': self.test_producer.id, 'tx_id': tx_id})
        self.assertEqual(response.status_code, 200)

        # producer can edit all parts of the lot
        j['tx_id'] = tx_id
        j['volume'] = 45000
        j['delivery_date'] = '2021-01-15'
        response = self.client.post(reverse('api-v3-update-lot'), j)
        self.assertEqual(response.status_code, 200)
        tx = LotTransaction.objects.get(id=tx_id)
        self.assertEqual(tx.lot.volume, 45000)
        self.assertEqual(tx.delivery_date, datetime.date(2021,1,15))
        self.assertEqual(tx.carbure_delivery_site.depot_id, '001')

        # send it back
        response = self.client.post(reverse('api-v3-validate-lot'), {'entity_id': self.test_producer.id, 'tx_ids': [tx_id]})
        self.assertEqual(response.status_code, 200)

        # accept lot
        response = self.client.post(reverse('api-v3-accept-lot'), {'entity_id': self.test_trader.id, 'tx_ids': [tx_id]})
        self.assertEqual(response.status_code, 200)

        # now start playing with fire
        # split lot, send it to a different client
        drafts = json.dumps([{'volume':5000, 'client': self.test_operator.name, 'dae':'DAESPLIT01', 'delivery_site':'001', 'delivery_date': '12/05/2021'}])
        response = self.client.post(reverse('api-v3-stocks-create-drafts'), {'entity_id': self.test_trader.id, 'drafts': drafts})
        self.assertEqual(response.status_code, 200)
        split_tx_id = response.json()['data']['tx_ids'][0]
        # it's a draft so parent volumes are unaffected
        split_tx = LotTransaction.objects.get(id=split_tx_id)
        self.assertEqual(split_tx.lot.status, LotV2.DRAFT)
        self.assertEqual(split_tx.delivery_status, LotTransaction.PENDING)
        self.assertEqual(split_tx.lot.parent_lot.remaining_volume, 45000)
        self.assertEqual(split_tx.lot.parent_lot.volume, 45000)

        # validate draft
        response = self.client.post(reverse('api-v3-stocks-send-drafts'), {'entity_id': self.test_trader.id, 'tx_ids':  [split_tx_id]})
        self.assertEqual(response.status_code, 200)
        # split is validated, stock is affected
        split_tx = LotTransaction.objects.get(id=split_tx_id)
        self.assertEqual(split_tx.lot.status, LotV2.VALIDATED)
        self.assertEqual(split_tx.delivery_status, LotTransaction.PENDING)
        self.assertEqual(split_tx.lot.parent_lot.remaining_volume, 40000)
        self.assertEqual(split_tx.lot.parent_lot.volume, 45000)


        # as final client, accept and request correction
        response = self.client.post(reverse('api-v3-accept-lot-with-reserves'), {'entity_id': self.test_operator.id, 'tx_ids': [split_tx_id]})
        self.assertEqual(response.status_code, 200)
        split_tx = LotTransaction.objects.get(id=split_tx_id)
        self.assertEqual(split_tx.lot.status, LotV2.VALIDATED)
        self.assertEqual(split_tx.delivery_status, LotTransaction.TOFIX)
        self.assertEqual(split_tx.lot.volume, 5000)
        self.assertEqual(split_tx.lot.remaining_volume, 5000)
        self.assertEqual(split_tx.lot.parent_lot.remaining_volume, 40000) # volume has not been re-credited because tx status is TOFIX
        self.assertEqual(split_tx.lot.parent_lot.volume, 45000)

        # as initial producer, try update lot and tx. nothing should work because it's a split. only the "master" or "parent" lot can be updated
        j['entity_id'] = self.test_producer.id
        j['tx_id'] = split_tx_id
        j['volume'] = 15000 # lot is split - volume can only be updated by trader
        j['pays_origine_code'] = 'DE'
        j['delivery_site'] = '002' # should not change
        response = self.client.post(reverse('api-v3-update-lot'), j)
        self.assertEqual(response.status_code, 200)
        split_tx = LotTransaction.objects.get(id=split_tx_id)
        self.assertEqual(split_tx.lot.volume, 5000) # volume is unchanged
        self.assertEqual(split_tx.lot.pays_origine.code_pays, 'FR') # pays_origine is unchanged
        self.assertEqual(split_tx.carbure_delivery_site.depot_id, '001') # delivery_site is unchanged
        
        
        # 3 as initial producer, send lot back to final client
        response = self.client.post(reverse('api-v3-validate-lot'), {'entity_id': self.test_producer.id, 'tx_ids': [split_tx_id]})
        self.assertEqual(response.status_code, 403) # only the intermediary can send it back
        # as the trader, send split lot back to client
        response = self.client.post(reverse('api-v3-validate-lot'), {'entity_id': self.test_trader.id, 'tx_ids': [split_tx_id]})
        self.assertEqual(response.status_code, 200)
        split_tx = LotTransaction.objects.get(id=split_tx_id)
        self.assertEqual(split_tx.lot.volume, 5000)
        self.assertEqual(split_tx.lot.remaining_volume, 5000)
        self.assertEqual(split_tx.lot.parent_lot.volume, 45000)
        self.assertEqual(split_tx.lot.parent_lot.remaining_volume, 40000)
        self.assertEqual(split_tx.delivery_status, LotTransaction.FIXED)

        # 4 as trader, re-open lot (amend-lot)
        response = self.client.post(reverse('api-v3-amend-lot'), {'entity_id': self.test_trader.id, 'tx_id': split_tx_id})
        self.assertEqual(response.status_code, 200)
        split_tx = LotTransaction.objects.get(id=split_tx_id)
        self.assertEqual(split_tx.lot.volume, 5000)
        self.assertEqual(split_tx.lot.remaining_volume, 5000)
        self.assertEqual(split_tx.lot.parent_lot.volume, 45000)
        self.assertEqual(split_tx.lot.parent_lot.remaining_volume, 40000)
        self.assertEqual(split_tx.delivery_status, LotTransaction.TOFIX)


        # 4 as trader, try update lot and tx, only tx should work
        j['entity_id'] = self.test_trader.id
        j['tx_id'] = split_tx_id
        j['volume'] = 5001 # volume change by the trader
        j['pays_origine_code'] = 'DE' # should not change
        j['delivery_site'] = '002' # should change
        response = self.client.post(reverse('api-v3-update-lot'), j)
        self.assertEqual(response.status_code, 200)

        split_tx = LotTransaction.objects.get(id=split_tx_id)
        self.assertEqual(split_tx.lot.pays_origine.code_pays, 'FR') # pays_origine has NOT been updated
        self.assertEqual(split_tx.carbure_delivery_site.depot_id, '002') # delivery_site has been updated
        self.assertEqual(split_tx.lot.volume, 5001)
        self.assertEqual(split_tx.lot.remaining_volume, 5001)
        self.assertEqual(split_tx.lot.parent_lot.volume, 45000)
        self.assertEqual(split_tx.lot.parent_lot.remaining_volume, 39999) # volume has been recredited when moved to "correction"
        self.assertEqual(split_tx.delivery_status, LotTransaction.TOFIX)

        # 5 send the lot back
        response = self.client.post(reverse('api-v3-validate-lot'), {'entity_id': self.test_trader.id, 'tx_ids': [split_tx_id]})
        self.assertEqual(response.status_code, 200)        
        split_tx = LotTransaction.objects.get(id=split_tx_id)
        self.assertEqual(split_tx.delivery_status, LotTransaction.FIXED)
        self.assertEqual(split_tx.lot.parent_lot.volume, 45000)
        self.assertEqual(split_tx.lot.parent_lot.remaining_volume, 39999)
