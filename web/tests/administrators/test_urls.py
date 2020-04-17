from django.test import TestCase
from django.urls import reverse
from producers.urls import urlpatterns
from django.contrib.auth import get_user_model

from core.models import Entity, UserRights
from producers.models import *

import datetime

class AdministratorsUrlsTest(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.operator = user_model.objects.create_user(email='testadmin@almalexia.org', name='DGEC TEST', password='totopouet42')
        self.entity, created = Entity.objects.update_or_create(name='DGEC', entity_type='Administration')
        right, created = UserRights.objects.update_or_create(user=self.operator, entity=self.entity)
        self.client.login(username='testadmin@almalexia.org', password='totopouet42')

    def test_index(self):
        response = self.client.get(reverse('administrators-settings'))
        self.assertEqual(response.status_code, 200)

    def test_controles(self):
        response = self.client.get(reverse('administrators-controles'))
        self.assertEqual(response.status_code, 200)

    def test_corrections(self):
        response = self.client.get(reverse('administrators-suivi-corrections'))
        self.assertEqual(response.status_code, 200)

    def test_certificats(self):
        response = self.client.get(reverse('administrators-suivi-certificats'))
        self.assertEqual(response.status_code, 200)

    def test_certificats_details(self):
        # need id
        response = self.client.get(reverse('administrators-certificate-details'))
        self.assertEqual(response.status_code, 200)

    def test_gestion_utilisateurs(self):
        response = self.client.get(reverse('administrators-gestion-utilisateurs'))
        self.assertEqual(response.status_code, 200)

    def test_settings(self):
        response = self.client.get(reverse('administrators-settings'))
        self.assertEqual(response.status_code, 200)