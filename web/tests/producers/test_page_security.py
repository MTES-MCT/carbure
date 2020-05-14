from django.test import TestCase
from django.urls import reverse
from producers.urls import urlpatterns
from django.contrib.auth import get_user_model

from core.models import Entity, UserRights
from producers.models import *
from django.core.files.base import ContentFile

import datetime

class TestOperatorsUrlsAsProducer(TestCase):
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

        # login with producer info
        self.client.login(username='testproducer@almalexia.org', password='totopouet42')

    #path('<slug:operator_name>/', views.operators_index, name='operators-index'),
    #path('<slug:operator_name>/declaration/<int:declaration_id>', views.operators_declaration, name='operators-declaration'),
    #path('<slug:operator_name>/affiliations', views.operators_affiliations, name='operators-affiliations'),
    #path('<slug:operator_name>/controles', views.operators_controles, name='operators-controles'),
    #path('<slug:operator_name>/settings', views.operators_settings, name='operators-settings'),

    def test_access_operators_index(self):
        response = self.client.get(reverse('operators-index', kwargs={'operator_name':self.operator_entity.url_friendly_name()}))
        self.assertEqual(response.status_code, 403)

    def test_access_operators_affiliations(self):
        response = self.client.get(reverse('operators-affiliations', kwargs={'operator_name':self.operator_entity.url_friendly_name()}))
        self.assertEqual(response.status_code, 403)

    def test_access_operators_controles(self):
        response = self.client.get(reverse('operators-controles', kwargs={'operator_name':self.operator_entity.url_friendly_name()}))
        self.assertEqual(response.status_code, 403)


class TestAdminUrlsAsProducer(TestCase):
    def setUp(self):
        user_model = get_user_model()
        # create a producer
        self.producer = user_model.objects.create_user(email='testproducer@almalexia.org', name='MP TEST', password='totopouet42')
        self.entity, created = Entity.objects.update_or_create(name='BioRaf1', entity_type='Producteur')
        right, created = UserRights.objects.update_or_create(user=self.producer, entity=self.entity)

        # create an admin
        self.admin = user_model.objects.create_user(email='testadmin@almalexia.org', name='DGEC TEST', password='totopouet42')
        self.admin_entity, created = Entity.objects.update_or_create(name='DGEC', entity_type='Administration')
        right, created = UserRights.objects.update_or_create(user=self.admin, entity=self.admin_entity)

        # login with producer info
        self.client.login(username='testproducer@almalexia.org', password='totopouet42')

    #path('', views.administrators_index, name='administrators-index'),
    #path('controles', views.administrators_controles, name='administrators-controles'),
    #path('suivi-corrections', views.administrators_suivi_corrections, name='administrators-suivi-corrections'),
    #path('suivi-certificats', views.administrators_suivi_certificats, name='administrators-suivi-certificats'),
    #path('suivi-certificats/<int:id>', views.administrators_certificate_details, name='administrators-certificate-details'),
    #path('gestion-utilisateurs', views.administrators_gestion_utilisateurs, name='administrators-gestion-utilisateurs'),
    #path('settings', views.administrators_settings, name='administrators-settings'),

    def test_access_admin_index(self):
        response = self.client.get(reverse('administrators-index'))
        self.assertEqual(response.status_code, 403)

    def test_access_admin_controles(self):
        response = self.client.get(reverse('administrators-controles'))
        self.assertEqual(response.status_code, 403)

    def test_access_admin_suivi_corrections(self):
        response = self.client.get(reverse('administrators-suivi-corrections'))
        self.assertEqual(response.status_code, 403)

    def test_access_admin_suivi_certificats(self):
        response = self.client.get(reverse('administrators-suivi-certificats'))
        self.assertEqual(response.status_code, 403)

    def test_access_admin_certif_details(self):
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

    def test_access_admin_gestion_utilisateurs(self):
        response = self.client.get(reverse('administrators-gestion-utilisateurs'))
        self.assertEqual(response.status_code, 403)

    def test_access_admin_settings(self):
        response = self.client.get(reverse('administrators-settings'))
        self.assertEqual(response.status_code, 403)
