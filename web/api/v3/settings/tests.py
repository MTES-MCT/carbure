from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from core.models import Entity, UserRights
from api.v3.admin.urls import urlpatterns


class SettingsAPITest(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user_email = 'testuser1@toto.com'
        self.user_password = 'totopouet'
        self.user1 = user_model.objects.create_user(email=self.user_email, name='Le Super Testeur 1', password=self.user_password)

        # a few entities
        self.entity1, _ = Entity.objects.update_or_create(name='Le Super Producteur 1', entity_type='Producteur')
        self.entity2, _ = Entity.objects.update_or_create(name='Le Super Operateur 1', entity_type='Opérateur')
        self.entity3, _ = Entity.objects.update_or_create(name='Le Super Trader 1', entity_type='Trader')

        # some rights
        UserRights.objects.update_or_create(user=self.user1, entity=self.entity1)
        UserRights.objects.update_or_create(user=self.user1, entity=self.entity2)         

        loggedin = self.client.login(username=self.user_email, password=self.user_password)
        self.assertTrue(loggedin)

    def test_get_settings(self):
        url = 'api-v3-settings-get'
        response = self.client.get(reverse(url))
        # api works
        self.assertEqual(response.status_code, 200)
        data = response.json()['data']
        self.assertIn('rights', data)
        self.assertIn('email', data)
        self.assertIn('requests', data)

    def test_mac_option(self):
        url_enable = 'api-v3-settings-enable-mac'
        url_disable = 'api-v3-settings-disable-mac'

        # wrongly formatted
        response = self.client.post(reverse(url_enable), {'entity_id':'blablabla'})
        self.assertEqual(response.status_code, 400)
        # no entity_id
        response = self.client.post(reverse(url_enable))
        self.assertEqual(response.status_code, 400)
        # entity I do not belong to
        response = self.client.post(reverse(url_enable), {'entity_id': self.entity3.id})
        self.assertEqual(response.status_code, 403)
        # should pass
        response = self.client.post(reverse(url_enable), {'entity_id': self.entity2.id})
        self.assertEqual(response.status_code, 200)
        entity = Entity.objects.get(id=self.entity2.id)
        self.assertEqual(entity.has_mac, True)

        # disable:
        # wrongly formatted
        response = self.client.post(reverse(url_disable), {'entity_id':'blablabla'})
        self.assertEqual(response.status_code, 400)
        # no entity_id
        response = self.client.post(reverse(url_disable))
        self.assertEqual(response.status_code, 400)
        # entity I do not belong to
        response = self.client.post(reverse(url_disable), {'entity_id': self.entity3.id})
        self.assertEqual(response.status_code, 403)
        # should pass
        response = self.client.post(reverse(url_disable), {'entity_id': self.entity2.id})
        self.assertEqual(response.status_code, 200)
        entity = Entity.objects.get(id=self.entity2.id)
        self.assertEqual(entity.has_mac, False)        

        # revert
        response = self.client.post(reverse(url_enable), {'entity_id': self.entity2.id})
        self.assertEqual(response.status_code, 200)
        entity = Entity.objects.get(id=self.entity2.id)
        self.assertEqual(entity.has_mac, True)

    def test_trading_option(self):
        url_enable = 'api-v3-settings-enable-trading'
        url_disable = 'api-v3-settings-disable-trading'

        # wrongly formatted
        response = self.client.post(reverse(url_enable), {'entity_id':'blablabla'})
        self.assertEqual(response.status_code, 400)
        # no entity_id
        response = self.client.post(reverse(url_enable))
        self.assertEqual(response.status_code, 400)
        # entity I do not belong to
        response = self.client.post(reverse(url_enable), {'entity_id': self.entity3.id})
        self.assertEqual(response.status_code, 403)
        # should pass
        response = self.client.post(reverse(url_enable), {'entity_id': self.entity1.id})
        self.assertEqual(response.status_code, 200)
        entity = Entity.objects.get(id=self.entity1.id)
        self.assertEqual(entity.has_trading, True)

        # disable:
        # wrongly formatted
        response = self.client.post(reverse(url_disable), {'entity_id':'blablabla'})
        self.assertEqual(response.status_code, 400)
        # no entity_id
        response = self.client.post(reverse(url_disable))
        self.assertEqual(response.status_code, 400)
        # entity I do not belong to
        response = self.client.post(reverse(url_disable), {'entity_id': self.entity3.id})
        self.assertEqual(response.status_code, 403)
        # should pass
        response = self.client.post(reverse(url_disable), {'entity_id': self.entity1.id})
        self.assertEqual(response.status_code, 200)
        entity = Entity.objects.get(id=self.entity1.id)
        self.assertEqual(entity.has_trading, False)        

        # revert
        response = self.client.post(reverse(url_enable), {'entity_id': self.entity1.id})
        self.assertEqual(response.status_code, 200)
        entity = Entity.objects.get(id=self.entity1.id)
        self.assertEqual(entity.has_trading, True)

        # should not work on Operator
        response = self.client.post(reverse(url_enable), {'entity_id': self.entity2.id})
        self.assertEqual(response.status_code, 400)        