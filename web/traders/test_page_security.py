from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from core.models import Entity, UserRights
from producers.models import *
from django.core.files.base import ContentFile

import datetime

from api.v2.producers.urls import urlpatterns as apiv2producersurls
from api.v2.operators.urls import urlpatterns as apiv2operatorsurls


class TestForbiddenUrlsAsTrader(TestCase):
    def setUp(self):
        user_model = get_user_model()
        # create a producer
        self.trader = user_model.objects.create_user(email='testtrader@almalexia.org', name='MP TEST', password='totopouet42')
        self.entity, created = Entity.objects.update_or_create(name='BioTrader1', entity_type='Trader')
        right, created = UserRights.objects.update_or_create(user=self.trader, entity=self.entity)

        # create a producer
        self.producer = user_model.objects.create_user(email='testproducer@almalexia.org', name='MP TEST', password='totopouet42')
        self.producer_entity, created = Entity.objects.update_or_create(name='BioRaf1', entity_type='Producteur')
        right, created = UserRights.objects.update_or_create(user=self.producer, entity=self.entity)

        # create an operator
        self.operator = user_model.objects.create_user(email='testoperator@almalexia.org', name='MP TEST', password='totopouet42')
        self.operator_entity, created = Entity.objects.update_or_create(name='PETRO1', entity_type='Opérateur')
        right, created = UserRights.objects.update_or_create(user=self.operator, entity=self.operator_entity)

        # create an admin
        self.admin = user_model.objects.create_user(email='testadmin@almalexia.org', name='DGEC TEST', password='totopouet42')
        self.admin_entity, created = Entity.objects.update_or_create(name='DGEC', entity_type='Administration')
        right, created = UserRights.objects.update_or_create(user=self.admin, entity=self.admin_entity)

        # login with producer info
        self.client.login(username='testproducer@almalexia.org', password='totopouet42')

    def test_access_producers_urls(self):
        response = self.client.get(reverse('producers-index', kwargs={'producer_name':self.producer_entity.url_friendly_name()}))
        self.assertEqual(response.status_code, 403)
        response = self.client.get(reverse('producers-mb', kwargs={'producer_name':self.producer_entity.url_friendly_name()}))
        self.assertEqual(response.status_code, 403)
        response = self.client.get(reverse('producers-histo', kwargs={'producer_name':self.producer_entity.url_friendly_name()}))
        self.assertEqual(response.status_code, 403)
        response = self.client.get(reverse('producers-controles', kwargs={'producer_name':self.producer_entity.url_friendly_name()}))
        self.assertEqual(response.status_code, 403)
        response = self.client.get(reverse('producers-settings', kwargs={'producer_name':self.producer_entity.url_friendly_name()}))
        self.assertEqual(response.status_code, 403)

    def test_access_operators_urls(self):
        response = self.client.get(reverse('operators-index', kwargs={'operator_name':self.operator_entity.url_friendly_name()}))
        self.assertEqual(response.status_code, 403)
        response = self.client.get(reverse('operators-controles', kwargs={'operator_name':self.operator_entity.url_friendly_name()}))
        self.assertEqual(response.status_code, 403)

    def test_access_admin_urls(self):
        response = self.client.get(reverse('administrators-index'))
        self.assertEqual(response.status_code, 403)
        response = self.client.get(reverse('administrators-controles'))
        self.assertEqual(response.status_code, 403)
        response = self.client.get(reverse('administrators-suivi-corrections'))
        self.assertEqual(response.status_code, 403)
        response = self.client.get(reverse('administrators-suivi-certificats'))
        self.assertEqual(response.status_code, 403)
        # create country
        p, created = Pays.objects.update_or_create(code_pays='VTN', name='Voituristan')
        # create production site
        ps, created = ProductionSite.objects.update_or_create(producer=self.entity, name='production-site-test', country=p, defaults={'date_mise_en_service':datetime.date.today()})
        # create certificate
        c, created = ProducerCertificate.objects.update_or_create(producer=self.entity, production_site=ps, certificate_id='TEST-CERTIF', defaults={'expiration':datetime.date.today()})
        c.certificate.save('django_test.txt', ContentFile(b'content'))
        # try to access certificate as an admin
        response = self.client.get(reverse('administrators-certificate-details', kwargs={'id':c.id}))
        self.assertEqual(response.status_code, 403)
        response = self.client.get(reverse('administrators-gestion-utilisateurs'))
        self.assertEqual(response.status_code, 403)

    def test_access_operators_api(self):
        for pattern in apiv2operatorsurls:
            response = self.client.get(reverse(pattern.name))
            self.assertEqual(response.status_code, 403)