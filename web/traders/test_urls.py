from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from core.models import Entity, UserRights


class TradersUrlsTest(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.trader = user_model.objects.create_user(email='testtrader@almalexia.org', name='MP TEST', password='totopouet42')
        self.entity, created = Entity.objects.update_or_create(name='BioTrader1', entity_type='Trader')
        right, created = UserRights.objects.update_or_create(user=self.trader, entity=self.entity)
        self.client.login(username='testtrader@almalexia.org', password='totopouet42')

    def test_index(self):
        response = self.client.get(reverse('traders-index',
                                           kwargs={'trader_name': self.entity.url_friendly_name()}))
        self.assertEqual(response.status_code, 200)
