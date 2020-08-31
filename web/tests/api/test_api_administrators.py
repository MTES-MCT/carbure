import json
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from core.models import Entity, UserRights


class AdminApiSecurityTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        # create a producer
        self.producer = user_model.objects.create_user(email='testproducer@almalexia.org', name='MP TEST', password='totopouet42')
        self.entity, created = Entity.objects.update_or_create(name='BioRaf1', entity_type='Producteur')
        right, created = UserRights.objects.update_or_create(user=self.producer, entity=self.entity)

        # create an operator
        self.operator = user_model.objects.create_user(email='testoperator@almalexia.org', name='MP TEST', password='totopouet42')
        self.operator_entity, created = Entity.objects.update_or_create(name='PETRO1', entity_type='Opérateur')
        right, created = UserRights.objects.update_or_create(user=self.operator, entity=self.operator_entity)

    def test_access_producer(self):
        self.client.login(username='testproducer@almalexia.org', password='totopouet42')
        response = self.client.get(reverse('admin-api-users-autocomplete'))
        self.assertEqual(response.status_code, 403)
        response = self.client.get(reverse('admin-api-entities-autocomplete'))
        self.assertEqual(response.status_code, 403)
        self.client.logout()

    def test_access_operator(self):
        self.client.login(username='testoperator@almalexia.org', password='totopouet42')
        response = self.client.get(reverse('admin-api-users-autocomplete'))
        self.assertEqual(response.status_code, 403)
        response = self.client.get(reverse('admin-api-entities-autocomplete'))
        self.assertEqual(response.status_code, 403)
        self.client.logout()


class AdminApiTest(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.admin = user_model.objects.create_user(email='testadmin@almalexia.org', name='DGEC TEST',
                                                    password='totopouet42')
        self.entity, created = Entity.objects.update_or_create(name='DGEC', entity_type='Administration')
        right, created = UserRights.objects.update_or_create(user=self.admin, entity=self.entity)
        self.client.login(username='testadmin@almalexia.org', password='totopouet42')

    def test_users_autcomplete(self):
        url = reverse('admin-api-users-autocomplete')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # make sure we can json load the response
        data = json.loads(response.content)

    def test_entities_autcomplete(self):
        url = reverse('admin-api-entities-autocomplete')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # make sure we can json load the response
        data = json.loads(response.content)
