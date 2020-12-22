import datetime
import os
import time
from django.test import TestCase
from django.test import TransactionTestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from core.models import Entity, UserRights, LotV2, LotTransaction, ProductionSite, Pays, Biocarburant, MatierePremiere, Depot
from api.v3.admin.urls import urlpatterns
from django_otp.plugins.otp_email.models import EmailDevice


class LotsAPITest(TransactionTestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user_email = 'testuser1@toto.com'
        self.user_password = 'totopouet'
        self.user1 = user_model.objects.create_user(email=self.user_email, name='Le Super Testeur 1', password=self.user_password)

        # a few entities
        self.entity1, _ = Entity.objects.update_or_create(name='Le Super Producteur 1', entity_type='Producteur')
        self.entity2, _ = Entity.objects.update_or_create(name='Le Super Operateur 1', entity_type='Opérateur')
        self.entity3, _ = Entity.objects.update_or_create(name='Le Super Trader 1', entity_type='Trader')

        # some rights
        UserRights.objects.update_or_create(user=self.user1, entity=self.entity1)
        UserRights.objects.update_or_create(user=self.user1, entity=self.entity2)         
        # note: user1 does not have access to entity3
        france, _ = Pays.objects.update_or_create(code_pays='FR', name='France')
        today = datetime.date.today()
        d = {'country': france, 'date_mise_en_service': today, 'site_id':'SIRET XXX',
        'city': 'paris', 'postal_code': '75001', 'manager_name':'Guillaume Caillou', 
        'manager_phone':'0145247000', 'manager_email': 'test@test.net'}
        self.production_site, _ = ProductionSite.objects.update_or_create(producer=self.entity1, name='Usine 001', defaults=d)
        Biocarburant.objects.update_or_create(code='ETH', name='Ethanol')
        MatierePremiere.objects.update_or_create(code='BT', name='Betterave')
        Depot.objects.update_or_create(name='Depot Test', depot_id='001', country=france)

        loggedin = self.client.login(username=self.user_email, password=self.user_password)
        self.assertTrue(loggedin)          
        # pass otp verification
        response = self.client.get(reverse('otp-verify'))
        self.assertEqual(response.status_code, 200)
        device = EmailDevice.objects.get(user=self.user1)
        response = self.client.post(reverse('otp-verify'), {'otp_token': device.token})
        self.assertEqual(response.status_code, 302)

    def test_lot_actions(self):
        # as producer / trader
        dae = 'TEST2020FR00923-094-32094'
        lot = {
            'production_site': self.production_site.name,
            'biocarburant_code': 'ETH',
            'matiere_premiere_code': 'BT',
            'volume': 15000,
            'pays_origine_code': 'FR',
            'ep': 20,
            'etd': 12,
            'dae': dae,
            'delivery_date': '2020-12-31',
            'client': self.entity2.name,
            'delivery_site': '001',
            'entity_id': self.entity1.id,
        }
        # add manual lot
        response = self.client.post(reverse('api-v3-add-lot'), lot)
        self.assertEqual(response.status_code, 200)  
        # update it
        tx = LotTransaction.objects.get(dae=dae)
        lot['ep'] = '21'
        lot['tx_id'] = tx.id
        response = self.client.post(reverse('api-v3-update-lot'), lot)
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('api-v3-lots-get-details'), {'entity_id': self.entity1.id, 'tx_id': tx.id})
        self.assertEqual(response.status_code, 200)        
        data = response.json()['data']
        self.assertEqual(data['transaction']['lot']['ep'], 21)
        # duplicate 3 times
        response = self.client.post(reverse('api-v3-duplicate-lot'), {'entity_id': self.entity1.id, 'tx_id': tx.id})
        response = self.client.post(reverse('api-v3-duplicate-lot'), {'entity_id': self.entity1.id, 'tx_id': tx.id})
        response = self.client.post(reverse('api-v3-duplicate-lot'), {'entity_id': self.entity1.id, 'tx_id': tx.id})               
        # delete 4th duplicate
        last = LotTransaction.objects.latest('id')
        response = self.client.post(reverse('api-v3-delete-lot'), {'entity_id': self.entity1.id, 'tx_ids':  [last.id]})
        self.assertEqual(response.status_code, 200)        
        # get drafts, make sure we have 3
        response = self.client.get(reverse('api-v3-lots-get'), {'entity_id': self.entity1.id, 'status': 'draft', 'year': '2020'})
        self.assertEqual(response.status_code, 200)        
        lots = response.json()['data']['lots']
        self.assertEqual(len(lots), 3)
        # update lots who do not have a dae
        for i, lot in enumerate(lots):
            if lot['dae'] == '':
                postdata = {
                    'tx_id': lot['id'],
                    'production_site': self.production_site.name,
                    'biocarburant_code': 'ETH',
                    'matiere_premiere_code': 'BT',
                    'volume': 15000,
                    'pays_origine_code': 'FR',
                    'ep': 20,
                    'etd': 12,
                    'dae': 'DAEUPDATED%d' % (i),
                    'delivery_date': '2020-12-31',
                    'client': self.entity2.name,
                    'delivery_site': '001',
                    'entity_id': self.entity1.id,
                }
                response = self.client.post(reverse('api-v3-update-lot'), postdata)
                self.assertEqual(response.status_code, 200)        

        # validate first lot
        response = self.client.post(reverse('api-v3-validate-lot'), {'entity_id': self.entity1.id, 'tx_ids': [tx.id]})
        self.assertEqual(response.status_code, 200)        
        # validate-all the rest
        response = self.client.post(reverse('api-v3-validate-all-drafts'), {'entity_id': self.entity1.id})
        self.assertEqual(response.status_code, 200)  
        # get drafts, make sure we have 0 - all sent
        response = self.client.get(reverse('api-v3-lots-get'), {'entity_id': self.entity1.id, 'status': 'draft', 'year': '2020'})
        self.assertEqual(response.status_code, 200)        
        data = response.json()['data']
        lots = data['lots']
        self.assertEqual(len(lots), 0)


        # as operator
        # make sure we received 3
        response = self.client.get(reverse('api-v3-lots-get'), {'entity_id': self.entity2.id, 'status': 'in', 'year': '2020'})
        self.assertEqual(response.status_code, 200)        
        lots = response.json()['data']['lots']
        self.assertEqual(len(lots), 3)    
        # reject first
        tx_id1 = lots[0]['id']
        response = self.client.post(reverse('api-v3-reject-lot'), {'entity_id': self.entity2.id, 'tx_ids': [tx_id1], 'comment': 'auto-reject-test'})
        self.assertEqual(response.status_code, 200)        
        # accept-with-reserves second + add comment
        tx_id2 = lots[1]['id']
        response = self.client.post(reverse('api-v3-accept-lot-with-reserves'), {'entity_id': self.entity2.id, 'tx_ids': [tx_id2]})
        self.assertEqual(response.status_code, 200)        
        # accept third
        tx_id3 = lots[2]['id']
        response = self.client.post(reverse('api-v3-accept-lot'), {'entity_id': self.entity2.id, 'tx_ids': [tx_id3]})
        self.assertEqual(response.status_code, 200)


    def test_producer_imports(self):
        return
        # as producer
        # upload 10 that cannot be validated
        file_directory = '%s/web/fixtures/csv/test_data' % (os.environ['CARBURE_HOME'])
        fh = open('%s/carbure_template_advanced_missing_data_cannot_validate.xlsx' % (file_directory), 'rb')
        response = self.client.post(reverse('api-v3-upload'), {'entity_id': self.entity2.id, 'file': fh})
        self.assertEqual(response.status_code, 200)
        fh.close()
        lots = LotV2.objects.filter(added_by_user=self.user1)
        self.assertEqual(lots.count(), 10)
        txs = LotTransaction.objects.filter(lot__in=lots)
        self.assertEqual(txs.count(), 10)
        # validate-all
        response = self.client.post(reverse('api-v3-validate-all-drafts'), {'entity_id': self.entity2.id})
        self.assertEqual(response.status_code, 200)
        # wait until process is finished
        time.sleep(5)
        # get drafts
        lots = LotV2.objects.filter(added_by_user=self.user1, status='Draft')
        self.assertEqual(lots.count(), 10) # they are still all with status draft
        # get drafts via api - same result expected
        response = self.client.get(reverse('api-v3-lots-get'), {'entity_id': self.entity1.id, 'status': 'draft', 'year': '2020'})
        self.assertEqual(response.status_code, 200)        
        data = response.json()['data']
        lots = data['lots']
        self.assertEqual(len(lots), 10)
        # make sure they all have LotError or TransactionError
        lot_errors = LotV2Error.objects.filter(lot__in=lots)
        tx_errors = TransactionError.objects.filter(tx__in=txs)
        nb_errors = lot_errors.count() + tx_errors.count()
        self.assertEqual(nb_errors, 10)
        # delete-all-drafts
        response = self.client.post(reverse('api-v3-delete-all-drafts'), {'entity_id': self.entity2.id})
        self.assertEqual(response.status_code, 200)               
        # make sure no lots/tx/loterror/txerror are still there
        self.assertEqual(LotV2Error.objects.all().count(), 0)
        self.assertEqual(TransactionError.objects.all().count(), 0)
        self.assertEqual(LotV2.objects.all().count(), 0)
        self.assertEqual(LotTransaction.objects.all().count(), 0)
        # upload 10 valid lots
        fh = open('%s/carbure_template_advanced_missing_data_but_valid.xlsx' % (file_directory), 'rb')
        response = self.client.post(reverse('api-v3-upload'), {'entity_id': self.entity2.id, 'file': fh})
        self.assertEqual(response.status_code, 200)
        fh.close()
        # validate-all
        response = self.client.post(reverse('api-v3-validate-all-drafts'), {'entity_id': self.entity2.id})
        self.assertEqual(response.status_code, 200)            
        # get drafts 0
        lots = LotV2.objects.filter(added_by_user=self.user1, status='Draft')
        self.assertEqual(lots.count(), 0) # no more drafts, all validated
        # check api
        response = self.client.get(reverse('api-v3-lots-get'), {'entity_id': self.entity1.id, 'status': 'draft', 'year': '2020'})
        self.assertEqual(response.status_code, 200)        
        data = response.json()['data']
        lots = data['lots']
        self.assertEqual(len(lots), 0)        
        # get validated 10
        lots = LotV2.objects.filter(added_by_user=self.user1, status='Validated')
        self.assertEqual(lots.count(), 10)
        # check api
        response = self.client.get(reverse('api-v3-lots-get'), {'entity_id': self.entity1.id, 'status': 'sent', 'year': '2020'})
        self.assertEqual(response.status_code, 200)        
        data = response.json()['data']
        lots = data['lots']
        self.assertEqual(len(lots), 10)

