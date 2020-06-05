import json
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from core.models import Entity, UserRights, Pays, Lot, MatierePremiere, Biocarburant
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
        d = {'ea_delivery_site':"osef", 'ea_delivery_date':"2012-12-12", "ea":self.operator_entity, "volume":10000, 'matiere_premiere':mp,
             'biocarburant':hvo, 'pays_origine':france, 'status':'Validated', 'ea_delivery_status':'A'}
        obj, created = Lot.objects.update_or_create(producer=entity, production_site=ps, dae="dae1", defaults=d)
        for i in range(4):
            obj.pk = None
            obj.dae = 'dae%d' % (i+1)
            obj.ea_delivery_status = 'N'
            obj.save()

    def test_get_declared_lots(self):
        url = reverse('operators-api-declared-lots')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # make sure we can json load the response
        data = json.loads(response.content)
        self.assertEqual(len(data), 1)
        #print('Lots déclarés')
        #print(data)

    def test_get_affiliated_lots(self):
        url = reverse('operators-api-affiliated-lots')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # make sure we can json load the response
        data = json.loads(response.content)
        self.assertEqual(len(data), 4)
        #print('Lots affiliés / en attente')
        #print(data)

    def test_accept_affiliated_lot(self):
        url = reverse('operators-api-affiliated-lots')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # make sure we can json load the response
        data = json.loads(response.content)
        lot = data[0]
        url = reverse('operators-api-accept-lots')
        res = self.client.post(url, {'lots':lot['lot_id']})
        self.assertEqual(res.status_code, 200)
        #print(res)
        url = reverse('operators-api-declared-lots')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # make sure we can json load the response
        data = json.loads(response.content)
        self.assertEqual(len(data), 2)

    def test_reject_affiliated_lot(self):
        url = reverse('operators-api-affiliated-lots')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # make sure we can json load the response
        data = json.loads(response.content)
        prevlen = len(data)
        lot = data[0]
        url = reverse('operators-api-reject-lots')
        res = self.client.post(url, {'lots':lot['lot_id'], 'comment':'rejected by automated testing'})
        self.assertEqual(res.status_code, 200)
        # check if we have lot less than before
        url = reverse('operators-api-affiliated-lots')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(prevlen-1, len(data))

    def test_accept_affiliated_lot_with_comment(self):
        url = reverse('operators-api-affiliated-lots')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # make sure we can json load the response
        data = json.loads(response.content)
        prevlen = len(data)
        lot = data[0]
        url = reverse('operators-api-accept-lot-with-comment')
        res = self.client.post(url, {'lot':lot['lot_id'], 'comment':'accept but please change XXX - automated testing'})
        self.assertEqual(res.status_code, 200)
        # check if we have lot less than before
        url = reverse('operators-api-affiliated-lots')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        # lot stays pending
        self.assertEqual(prevlen, len(data))

    def test_lot_with_comment(self):
        url = reverse('operators-api-affiliated-lots')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # make sure we can json load the response
        data = json.loads(response.content)
        lot = data[0]
        url = reverse('operators-api-accept-lot-with-comment')
        res = self.client.post(url, {'lot':lot['lot_id'], 'comment':'accept but please change XXX - automated testing'})
        self.assertEqual(res.status_code, 200)
        # check if we have lot less than before
        url = reverse('operators-api-lot-comments')
        response = self.client.post(url, {'lot_id': lot['lot_id']})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        # check that we do have a comment
        self.assertEqual(len(data), 1)

    def test_export(self):
        url = reverse('operators-api-declaration-export')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # just make sure the response isn't empty
        self.assertEqual(len(response.content) > 10, True)

        url = reverse('operators-api-export-affiliated')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # just make sure the response isn't empty
        self.assertEqual(len(response.content) > 10, True)

    def test_accept_corrected_lot(self):
        url = reverse('operators-api-affiliated-lots')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # make sure we can json load the response
        data = json.loads(response.content)
        prevlen = len(data)
        lot = data[0]
        url = reverse('operators-api-accept-lot-correction')
        res = self.client.post(url, {'lot': lot['lot_id']})
        self.assertEqual(res.status_code, 200)

        # check if we have lot less than before
        url = reverse('operators-api-affiliated-lots')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        # lot stays pending
        self.assertEqual(prevlen - 1, len(data))
