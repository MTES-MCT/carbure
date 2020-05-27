import json
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from core.models import Entity, UserRights
from api.urls import urlpatterns

#path('operators/lots/accept', operators_api.operators_lot_accept, name='operators-api-accept-lots'),
#path('operators/lots/accept-correction', operators_api.operators_lot_accept_correction, name='operators-api-accept-lot-correction'),
#path('operators/lots/accept-with-comment', operators_api.operators_lot_accept_with_comment, name='operators-api-accept-lot-with-comment'),
#path('operators/lots/reject', operators_api.operators_lot_reject, name='operators-api-reject-lots'),
#path('operators/lots/comments', operators_api.operators_lot_comments, name='operators-api-lot-comments'),
#path('operators/lots/export', operators_api.operators_export_lots, name='operators-api-declaration-export'),


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
            if p.name.startswith('operator'):
                response = self.client.get(reverse(p.name))
                self.assertEqual(response.status_code, 403)
        self.client.logout()

    def test_access_admin(self):
        self.client.login(username='testadmin@almalexia.org', password='totopouet42')
        for p in urlpatterns:
            if p.name.startswith('operator'):
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

    def test_get_declared_lots(self):
        url = reverse('operators-api-declared-lots')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # make sure we can json load the response
        data = json.loads(response.content)

    def test_get_affiliated_lots(self):
        url = reverse('operators-api-affiliated-lots')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # make sure we can json load the response
        data = json.loads(response.content)

    def test_accept_affiliated_lot(self):
        url = reverse('operators-api-affiliated-lots')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # make sure we can json load the response
        data = json.loads(response.content)
