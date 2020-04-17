from django.test import TestCase
from django.urls import reverse
from producers.urls import urlpatterns
from django.contrib.auth import get_user_model

from core.models import Entity, UserRights
from operators.models import *

import datetime

class OperatorsUrlsTest(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.operator = user_model.objects.create_user(email='testoperator@almalexia.org', name='MP TEST', password='totopouet42')
        self.entity, created = Entity.objects.update_or_create(name='PETRO1', entity_type='Opérateur')
        right, created = UserRights.objects.update_or_create(user=self.operator, entity=self.entity)
        self.client.login(username='testoperator@almalexia.org', password='totopouet42')

    def test_index(self):
        response = self.client.get(reverse('operators-index', kwargs={'operator_name':'PETRO1'}))
        self.assertEqual(response.status_code, 200)
        declarations = OperatorDeclaration.objects.filter(operator=self.entity)
        response = self.client.get(reverse('operators-declaration', kwargs={'operator_name':'PETRO1', 'declaration_id':declarations[0].id}))
        self.assertEqual(response.status_code, 200)

    def test_affiliations(self):
        response = self.client.get(reverse('operators-affiliations', kwargs={'operator_name':'PETRO1'}))
        self.assertEqual(response.status_code, 200)

    def test_controles(self):
        response = self.client.get(reverse('operators-controles', kwargs={'operator_name':'PETRO1'}))
        self.assertEqual(response.status_code, 200)

    def test_settings(self):
        response = self.client.get(reverse('operators-settings', kwargs={'operator_name':'PETRO1'}))
        self.assertEqual(response.status_code, 200)


