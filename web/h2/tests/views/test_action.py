from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from core.models import Entity
from core.tests_utils import setup_current_user
from traceability.factories import ActionFactory
from traceability.models import Action


class H2ActionAccessTest(TestCase):
    fixtures = ["json/countries.json"]

    def setUp(self):
        self.hrs = Entity.objects.create(name="HRS", entity_type=Entity.HRS)
        self.producer = Entity.objects.create(name="Producer", entity_type=Entity.PRODUCER)
        self.list_url = reverse("traceability-action-list")

    def test_producer_cannot_access_h2_actions(self):
        setup_current_user(self, "producer@carbure.local", "Producer", "password", [(self.producer, "RW")])
        action = ActionFactory.create(holder=self.hrs, industry=Action.H2)

        response = self.client.get(
            self.list_url,
            {"entity_id": self.producer.id, "industry": Action.H2},
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.get(
            reverse("traceability-action-detail", kwargs={"pk": action.pk}),
            {"entity_id": self.producer.id, "industry": Action.H2},
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_hrs_readonly_cannot_write_h2_actions(self):
        setup_current_user(self, "reader@carbure.local", "Reader", "password", [(self.hrs, "RO")])
        action = ActionFactory.create(holder=self.hrs, industry=Action.H2)
        params = {"entity_id": self.hrs.id, "industry": Action.H2}

        list_response = self.client.get(self.list_url, params)
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)

        create_response = self.client.post(
            self.list_url,
            {},
            content_type="application/json",
            query_params=params,
        )
        self.assertEqual(create_response.status_code, status.HTTP_403_FORBIDDEN)

        delete_response = self.client.delete(
            reverse("traceability-action-detail", kwargs={"pk": action.pk}),
            query_params=params,
        )
        self.assertEqual(delete_response.status_code, status.HTTP_403_FORBIDDEN)
