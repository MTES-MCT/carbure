from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from core.models import Entity, UserRights
from api.v4.tests_utils import setup_current_user

User = get_user_model()


class Endpoint:
    change_user_role = reverse('api-v4-settings-change-user-role')

class SettingsTest(TestCase):
    def setUp(self):
        # let's create a user with some rights
        self.entity = Entity.objects.create(name="Test entity", entity_type=Entity.TRADER)
        self.user = setup_current_user(self, 'test@carbure.test', 'Tester', 'gogogo', [(self.entity, 'ADMIN')])

    def test_change_user_role_missing_params(self):
        res = self.client.post(Endpoint.change_user_role, {'email': self.user.email, 'entity_id': self.entity.id})
        self.assertEqual(res.status_code, 400)
        data = res.json()
        self.assertEqual(data['error'], 'MISSING_PARAMS')

    def test_change_user_role_missing_user(self):
        res = self.client.post(Endpoint.change_user_role, {'email': 'missing@carbure.test', 'entity_id': self.entity.id, 'role': 'RW'})
        self.assertEqual(res.status_code, 404)
        data = res.json()
        self.assertEqual(data['error'], 'MISSING_USER')

    def test_change_user_role_no_prior_rights(self):
        other_user = User.objects.create(email='other@carbure.test', name='Other', password='other')
        res = self.client.post(Endpoint.change_user_role, {'email': other_user.email, 'entity_id': self.entity.id, 'role': 'RW'})
        self.assertEqual(res.status_code, 400)
        data = res.json()
        self.assertEqual(data['error'], 'NO_PRIOR_RIGHTS')

    def test_change_user_role_ok(self):
        user_right = UserRights.objects.get(user=self.user, entity=self.entity)
        self.assertEqual(user_right.role, 'ADMIN')
        res = self.client.post(Endpoint.change_user_role, {'email': self.user.email, 'entity_id': self.entity.id, 'role': 'RW'})
        self.assertEqual(res.status_code, 200)
        user_right = UserRights.objects.get(user=self.user, entity=self.entity)
        self.assertEqual(user_right.role, 'RW')





