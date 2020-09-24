from django.test import TestCase
from django.urls import reverse
from producers.urls import urlpatterns
from django.contrib.auth import get_user_model

from core.models import Entity, UserRights
from producers.models import *

import datetime

class RestrictedUrlsTest(TestCase):
    # only accessible to logged in users, redirect to login page
    def test_annuaire(self):
        response = self.client.get(reverse('annuaire'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/accounts/login/?next=/public/annuaire")

    # only accessible to logged in users, redirect to login page
    def test_home(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/accounts/login/?next=/public/home")

class RestrictedUrlsTestLoggedinProducer(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.producer = user_model.objects.create_user(email='testproducer@almalexia.org', name='MP TEST', password='totopouet42')
        self.entity, created = Entity.objects.update_or_create(name='BioRaf1', entity_type='Producteur')
        right, created = UserRights.objects.update_or_create(user=self.producer, entity=self.entity)
        self.client.login(username='testproducer@almalexia.org', password='totopouet42')

    def test_annuaire_loggedin(self):
        response = self.client.get(reverse('annuaire'))
        self.assertEqual(response.status_code, 200)

    def test_home_loggedin(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/producers/v2/BIORAF1/")

class RestrictedUrlsTestLoggedinOperator(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.operator = user_model.objects.create_user(email='testoperator@almalexia.org', name='OP TEST', password='totopouet42')
        self.entity, created = Entity.objects.update_or_create(name='PetroPerateur1', entity_type='Opérateur')
        right, created = UserRights.objects.update_or_create(user=self.operator, entity=self.entity)
        self.client.login(username='testoperator@almalexia.org', password='totopouet42')

    def test_annuaire_loggedin(self):
        response = self.client.get(reverse('annuaire'))
        self.assertEqual(response.status_code, 200)

    def test_home_loggedin(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/operators/PETROPERATEUR1/")

class RestrictedUrlsTestLoggedinAdministrator(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.operator = user_model.objects.create_user(email='testadmin@almalexia.org', name='DGEC TEST', password='totopouet42')
        self.entity, created = Entity.objects.update_or_create(name='DGEC', entity_type='Administration')
        right, created = UserRights.objects.update_or_create(user=self.operator, entity=self.entity)
        self.client.login(username='testadmin@almalexia.org', password='totopouet42')

    def test_annuaire_loggedin(self):
        response = self.client.get(reverse('annuaire'))
        self.assertEqual(response.status_code, 200)

    def test_home_loggedin(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/administrators/")

class RestrictedUrlsTestLoggedinUnknown(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.operator = user_model.objects.create_user(email='testunknown@almalexia.org', name='David Copperfield', password='totopouet42')
        self.entity, created = Entity.objects.update_or_create(name='HAHA', entity_type='Magician')
        right, created = UserRights.objects.update_or_create(user=self.operator, entity=self.entity)
        self.client.login(username='testunknown@almalexia.org', password='totopouet42')

    def test_annuaire_loggedin(self):
        response = self.client.get(reverse('annuaire'))
        self.assertEqual(response.status_code, 200)

    def test_home_loggedin(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 404)
