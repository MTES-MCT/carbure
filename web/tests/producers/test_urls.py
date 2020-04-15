from django.test import TestCase
from django.urls import reverse
from producers.urls import urlpatterns
from django.contrib.auth import get_user_model

from core.models import Entity, UserRights

class ProducersTest(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.producer = user_model.objects.create_user(email='testproducer@almalexia.org', name='MP TEST', password='totopouet42')
        self.entity, created = Entity.objects.update_or_create(name='BioRaf1', entity_type='Producteur')
        right, created = UserRights.objects.update_or_create(user=self.producer, entity=self.entity)

    def test_login(self):
        self.client.login(username='testproducer@almalexia.org', password='totopouet42')

        for url in urlpatterns:
            print(url)
            response = self.client.get(reverse(url.name, kwargs={'producer_name':self.entity.url_friendly_name()}))
            self.assertEqual(response.status_code, 200)

