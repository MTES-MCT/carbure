from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from core.models import Entity, UserRights


class ProducersUrlsTest(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.producer = user_model.objects.create_user(email='testproducer@almalexia.org', name='MP TEST',
                                                       password='totopouet42')
        self.entity, created = Entity.objects.update_or_create(name='BioRaf1', entity_type='Producteur')
        right, created = UserRights.objects.update_or_create(user=self.producer, entity=self.entity)
        self.client.login(username='testproducer@almalexia.org', password='totopouet42')

    def test_index(self):
        response = self.client.get(reverse('producers-index',
                                           kwargs={'producer_name': self.entity.url_friendly_name()}))
        self.assertEqual(response.status_code, 200)

    def test_settings(self):
        response = self.client.get(reverse('producers-settings',
                                           kwargs={'producer_name': self.entity.url_friendly_name()}))
        self.assertEqual(response.status_code, 200)

    def test_controles(self):
        response = self.client.get(reverse('producers-controles',
                                           kwargs={'producer_name': self.entity.url_friendly_name()}))
        self.assertEqual(response.status_code, 200)
