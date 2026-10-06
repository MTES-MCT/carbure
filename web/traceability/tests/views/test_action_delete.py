from urllib.parse import urlencode

from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from core.models import Entity
from core.tests_utils import setup_current_user
from traceability.factories import ActionFactory
from traceability.models import Action, ActionStatus


class ActionDeleteTest(TestCase):
    def setUp(self):
        self.entity = Entity.objects.create(name="HRS", entity_type=Entity.HRS)
        self.other_entity = Entity.objects.create(name="Other HRS", entity_type=Entity.HRS)
        setup_current_user(self, "tester@carbure.local", "Tester", "password", [(self.entity, "RW")])
        self.base_params = {"entity_id": self.entity.id, "industry": Action.H2}

    def delete_url(self, action):
        return reverse("traceability-action-detail", args=[action.id])

    def delete(self, action):
        return self.client.delete(self.delete_url(action), QUERY_STRING=urlencode(self.base_params))

    def create_action(self, **kwargs):
        return ActionFactory.create(
            holder=self.entity,
            industry=Action.H2,
            parent=None,
            material=None,
            site=None,
            **kwargs,
        )

    def test_deletes_init_action_when_status_is_pending(self):
        action = self.create_action(type=Action.INIT, status=ActionStatus.PENDING)

        response = self.delete(action)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Action.unannotated.filter(pk=action.pk).exists())
        self.assertFalse(ActionStatus.objects.filter(action_id=action.pk).exists())

    def test_deletes_init_action_when_status_is_rejected(self):
        action = self.create_action(type=Action.INIT, status=ActionStatus.REJECTED)

        response = self.delete(action)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Action.unannotated.filter(pk=action.pk).exists())

    def test_keeps_init_action_when_status_is_accepted(self):
        action = self.create_action(type=Action.INIT, status=ActionStatus.ACCEPTED)

        response = self.delete(action)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(Action.unannotated.filter(pk=action.pk).exists())

    def test_keeps_init_action_when_status_is_created(self):
        action = self.create_action(type=Action.INIT, status=ActionStatus.CREATED)

        response = self.delete(action)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(Action.unannotated.filter(pk=action.pk).exists())

    def test_keeps_valorize_action_even_when_status_is_pending(self):
        action = self.create_action(type=Action.VALORIZE, status=ActionStatus.PENDING)

        response = self.delete(action)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(Action.unannotated.filter(pk=action.pk).exists())

    def test_returns_not_found_when_action_is_held_by_another_entity(self):
        action = ActionFactory.create(
            holder=self.other_entity,
            industry=Action.H2,
            parent=None,
            material=None,
            site=None,
            type=Action.INIT,
            status=ActionStatus.PENDING,
        )

        response = self.delete(action)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Action.unannotated.filter(pk=action.pk).exists())

    def test_returns_forbidden_when_user_has_read_only_rights(self):
        setup_current_user(self, "reader@carbure.local", "Reader", "password", [(self.entity, "RO")])
        action = self.create_action(type=Action.INIT, status=ActionStatus.PENDING)

        response = self.delete(action)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Action.unannotated.filter(pk=action.pk).exists())
