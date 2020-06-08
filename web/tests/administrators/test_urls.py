from django.test import TestCase
from django.urls import reverse
from producers.urls import urlpatterns
from django.contrib.auth import get_user_model
from unittest.mock import Mock, MagicMock
from core.models import Entity, UserRights
from producers.models import *
import django
import datetime
from django.core.files.base import ContentFile


class AdministratorsUrlsTest(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.operator = user_model.objects.create_user(email='testadmin@almalexia.org', name='DGEC TEST', password='totopouet42')
        self.entity, created = Entity.objects.update_or_create(name='DGEC', entity_type='Administration')
        right, created = UserRights.objects.update_or_create(user=self.operator, entity=self.entity)
        self.client.login(username='testadmin@almalexia.org', password='totopouet42')
        Pays.objects.update_or_create(code_pays='FR', name='France')
        Biocarburant.objects.update_or_create(code='ET', name='Ethanol')
        Biocarburant.objects.update_or_create(code='EMHV', name='EMHV')
        Biocarburant.objects.update_or_create(code='EMHU', name='EMHU')
        Biocarburant.objects.update_or_create(code='EMHA', name='EMHA')
        MatierePremiere.objects.update_or_create(code='COLZA', name='Colza')
        MatierePremiere.objects.update_or_create(code='TOURNESOL', name='Tournesol')
        MatierePremiere.objects.update_or_create(code='SOJA', name='Soja')
        MatierePremiere.objects.update_or_create(code='HUILE_ALIMENTAIRE_USAGEE', name='HAU')
        MatierePremiere.objects.update_or_create(code='HUILES_OU_GRAISSES_ANIMALES_CAT1_CAT2', name='Graisses animales c1/c2')
        MatierePremiere.objects.update_or_create(code='BETTERAVE', name='Betterave')
        MatierePremiere.objects.update_or_create(code='BLE', name='Ble')
        MatierePremiere.objects.update_or_create(code='MAIS', name='Mais')
        MatierePremiere.objects.update_or_create(code='RESIDUS_VINIQUES', name='Residus viniques')

    def test_index(self):
        response = self.client.get(reverse('administrators-index'))
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
        # create a producer
        user_model = get_user_model()
        self.producer = user_model.objects.create_user(email='testproducer@almalexia.org', name='MP TEST', password='totopouet42')
        self.producer_entity, created = Entity.objects.update_or_create(name='BioRaf1', entity_type='Producteur')
        right, created = UserRights.objects.update_or_create(user=self.producer, entity=self.producer_entity)
        # create country
        p, created = Pays.objects.update_or_create(code_pays='VTN', name='Voituristan')
        # create production site
        ps, created = ProductionSite.objects.update_or_create(producer=self.producer_entity, name='production-site-test', country=p, defaults={'date_mise_en_service':datetime.date.today()})
        # create certificate
        c, created = ProducerCertificate.objects.update_or_create(producer=self.producer_entity, production_site=ps, certificate_id='TEST-CERTIF', defaults={'expiration':datetime.date.today()})
        c.certificate.save('django_test.txt', ContentFile(b'content'))
        # check certificate
        response = self.client.get(reverse('administrators-certificate-details', kwargs={'id':c.id}))
        self.assertEqual(response.status_code, 200)

    def test_gestion_utilisateurs(self):
        response = self.client.get(reverse('administrators-gestion-utilisateurs'))
        self.assertEqual(response.status_code, 200)
