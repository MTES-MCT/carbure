from django.test import TestCase
from django.urls import reverse
from producers.urls import urlpatterns
from django.contrib.auth import get_user_model

from core.models import Entity, UserRights, Pays, Biocarburant, MatierePremiere
from producers.models import *

import datetime

class PublicUrlsTest(TestCase):
    def setUp(self):
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
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)

    def test_stats(self):
        response = self.client.get(reverse('public-stats'))
        self.assertEqual(response.status_code, 200)
