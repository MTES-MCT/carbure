import json
import datetime

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from core.models import Entity, UserRights, Pays, LotV2, LotTransaction, MatierePremiere, Biocarburant
from producers.models import ProductionSite
from api.urls import urlpatterns


class OperatorsApiSecurityTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        # create a producer
        self.producer = user_model.objects.create_user(email='testproducer@almalexia.org', name='MP TEST',
                                                       password='totopouet42')
        self.entity, created = Entity.objects.update_or_create(name='BioRaf1', entity_type='Producteur')
        right, created = UserRights.objects.update_or_create(user=self.producer, entity=self.entity)

        # create an administrator
        self.admin = user_model.objects.create_user(email='testadmin@almalexia.org', name='DGEC TEST',
                                                    password='totopouet42')
        self.entity, created = Entity.objects.update_or_create(name='DGEC', entity_type='Administration')
        right, created = UserRights.objects.update_or_create(user=self.admin, entity=self.entity)

    def test_access_producer(self):
        self.client.login(username='testproducer@almalexia.org', password='totopouet42')
        for p in urlpatterns:
            if hasattr(p, 'name') and p.name.startswith('operator'):
                response = self.client.get(reverse(p.name))
                self.assertEqual(response.status_code, 403)
        self.client.logout()

    def test_access_admin(self):
        self.client.login(username='testadmin@almalexia.org', password='totopouet42')
        for p in urlpatterns:
            if hasattr(p, 'name') and p.name.startswith('operator'):
                response = self.client.get(reverse(p.name))
                self.assertEqual(response.status_code, 403)
        self.client.logout()


class OperatorsApiTest(TestCase):
    def setUp(self):
        user_model = get_user_model()
        # create an operator
        self.operator = user_model.objects.create_user(email='testoperator@almalexia.org', name='MP TEST', password='totopouet42')
        self.operator_entity, created = Entity.objects.update_or_create(name='PETRO1', entity_type='Opérateur')
        right, created = UserRights.objects.update_or_create(user=self.operator, entity=self.operator_entity)
        self.client.login(username='testoperator@almalexia.org', password='totopouet42')

        # create data for testcases:
        # we want 4 lots
        # - one declared
        # - one to accept
        # - one to request changes
        # - one to reject
        # - one to accept with a comment
        # login as a producer, use api to create and assign lots
        self.producer = user_model.objects.create_user(email='testproducer@almalexia.org', name='MP TEST',
                                                       password='totopouet42')
        entity, created = Entity.objects.update_or_create(name='BioRaf1', entity_type='Producteur')
        right, created = UserRights.objects.update_or_create(user=self.producer, entity=entity)
        france, created = Pays.objects.update_or_create(code_pays='FR', defaults={'name': 'France'})
        ps, created = ProductionSite.objects.update_or_create(producer=entity, name="BIORAF1_USINE1", country=france, date_mise_en_service="2012-12-12")
        mp, created = MatierePremiere.objects.update_or_create(name='Colza', code='COLZA')
        hvo, created = Biocarburant.objects.update_or_create(code='HVO', defaults={'code':'HVO'})

        # create a lot. valid and declared
        d = {'period':"2020-06", 'carbure_id':"TESTFR0001XXX", "producer_is_in_carbure": True, "unknown_producer": "",
        "production_site_is_in_carbure": True, "unknown_production_site":"", "unknown_production_country": None, "unknown_production_site_com_date": None,
        "unknown_production_site_reference": "", "unknown_production_site_dbl_counting": "", "volume":10000, 'matiere_premiere': mp, 'biocarburant':hvo, 'pays_origine':france,
        'status':'Validated', 'source':'AUTOMATEDTEST', "added_by": entity, "added_by_user": self.producer}
        obj, created = LotV2.objects.update_or_create(carbure_producer=entity, carbure_production_site=ps, defaults=d)

        dd = datetime.date.today()
        d = {'vendor_is_in_carbure': True, 'carbure_vendor': entity, "unknown_vendor":"", 'client_is_in_carbure':True, 'carbure_client':self.operator_entity, 'delivery_date':dd,
        'delivery_site_is_in_carbure': False, 'unknown_delivery_site':'TESTDELIVERYSITE', 'unknown_delivery_site_country': france, 'delivery_status': 'A'}
        tx, created = LotTransaction.objects.update_or_create(lot=obj, dae="dae1", defaults=d)

        # create several drafts
        for i in range(4):
            obj.pk = None
            obj.volume += 1
            obj.save()

            tx.pk = None
            tx.lot = obj
            tx.dae = 'dae%d' % (i+1)
            tx.delivery_status = 'N'
            tx.save()

    def test_get_out(self):
        url = reverse('api-v2-operators-get-out')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # make sure we can json load the response
        data = json.loads(response.content)
        txs = json.loads(data['transactions'])
        self.assertEqual(len(txs), 1)

    def test_get_in(self):
        url = reverse('api-v2-operators-get-in')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # make sure we can json load the response
        data = json.loads(response.content)
        txs = json.loads(data['transactions'])
        self.assertEqual(len(txs), 4)

    def test_accept_in(self):
        # get validated txs and check len
        url = reverse('api-v2-operators-get-out')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        txs = json.loads(data['transactions'])
        prev_len_out = len(txs)

        # get pending txs and accept one
        url = reverse('api-v2-operators-get-in')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        txs = json.loads(data['transactions'])
        tx = txs[0]
        url = reverse('api-v2-operators-accept-lots')
        res = self.client.post(url, {'tx_ids':tx['pk']})
        self.assertEqual(res.status_code, 200)

        # check if validated txs has incremented by one
        url = reverse('api-v2-operators-get-out')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        txs_out = json.loads(data['transactions'])
        self.assertEqual(prev_len_out + 1, len(txs_out))

    def test_reject_in(self):
        # check pending lots len
        url = reverse('api-v2-operators-get-in')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        txs = json.loads(data['transactions'])
        prevlen = len(txs)
        tx = txs[0]

        # reject one
        url = reverse('api-v2-operators-reject-lot')
        res = self.client.post(url, {'tx_id':tx['pk'], 'comment':'rejected by automated testing'})
        self.assertEqual(res.status_code, 200)

        # check if we have a tx less than before
        url = reverse('api-v2-operators-get-in')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(prevlen-1, len(data))

    def test_accept_tx_with_comment(self):
        url = reverse('api-v2-operators-get-in')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # make sure we can json load the response
        data = json.loads(response.content)
        txs = json.loads(data['transactions'])
        prevlen = len(txs)
        tx = txs[0]

        url = reverse('api-v2-operators-accept-lot-with-correction')
        res = self.client.post(url, {'tx_id':tx['pk'], 'comment':'accept but please change XXX - automated testing'})
        self.assertEqual(res.status_code, 200)

        # check if we still have the TX but with status 'AC'
        url = reverse('api-v2-operators-get-in')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        newtxs = json.loads(data['transactions'])
        comments = json.loads(data['comments'])
        # lot stays pending
        self.assertEqual(prevlen, len(newtxs))
        found = False
        for ntx in newtxs:
            if ntx['pk'] == tx['pk']:
                found = True
                # check if the status has changed
                self.assertEqual(ntx['fields']['delivery_status'], 'AC')
        self.assertEqual(found, True)
        found = False
        for comment in comments:
            if comment['fields']['tx'] == tx['pk']:
                found = True

    def test_export(self):
        url = reverse('api-v2-operators-export-out')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # just make sure the response isn't empty
        self.assertEqual(len(response.content) > 10, True)

        url = reverse('api-v2-operators-export-in')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # just make sure the response isn't empty
        self.assertEqual(len(response.content) > 10, True)

        url = reverse('api-v2-operators-export-drafts')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # just make sure the response isn't empty
        self.assertEqual(len(response.content) > 10, True)
