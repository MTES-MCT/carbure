from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from core.models import Entity
from core.tests_utils import setup_current_user
from traceability.factories import ActionFactory
from traceability.models import Action


class ActionViewsetAccessTest(TestCase):
    fixtures = ["json/countries.json"]

    def setUp(self):
        self.entity = Entity.objects.create(name="HRS", entity_type=Entity.HRS)
        self.other_entity = Entity.objects.create(name="Other HRS", entity_type=Entity.HRS)
        setup_current_user(self, "tester@carbure.local", "Tester", "password", [(self.entity, "RW")])

        self.list_url = reverse("traceability-action-list")
        self.base_params = {"entity_id": self.entity.id, "industry": Action.H2}

        self.own_action = ActionFactory.create(holder=self.entity, industry=Action.H2)
        self.other_holder_action = ActionFactory.create(holder=self.other_entity, industry=Action.H2)
        self.other_industry_action = ActionFactory.create(holder=self.entity, industry="BIOMASS")

    def _detail_url(self, action):
        return reverse("traceability-action-detail", kwargs={"pk": action.pk})

    def _payload(self, **overrides):
        data = {
            "pos_id": "POS-WRITE-001",
            "type": Action.INIT,
            "material": self.own_action.material_id,
            "quantity": "10.000",
            "site": self.own_action.site_id,
            "shipping_date": "2026-01-15",
            "shipping_distance": 12,
            "shipping_method": Action.ROAD,
            "working_date": "2026-01-15",
        }
        data.update(overrides)
        return data

    def test_list_is_scoped_to_the_entity_and_industry(self):
        response = self.client.get(self.list_url, self.base_params)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual([item["id"] for item in response.data["results"]], [self.own_action.id])

    def test_retrieve_own_action(self):
        response = self.client.get(self._detail_url(self.own_action), self.base_params)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.own_action.id)

    def test_cannot_retrieve_another_entity_action(self):
        response = self.client.get(self._detail_url(self.other_holder_action), self.base_params)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_cannot_retrieve_another_industry_action(self):
        response = self.client.get(self._detail_url(self.other_industry_action), self.base_params)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_cannot_update_another_entity_action(self):
        response = self.client.patch(
            self._detail_url(self.other_holder_action),
            {"quantity": "99.000"},
            content_type="application/json",
            query_params=self.base_params,
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_cannot_destroy_another_entity_action(self):
        response = self.client.delete(self._detail_url(self.other_holder_action), query_params=self.base_params)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Action.objects.filter(pk=self.other_holder_action.pk).exists())

    def test_create_uses_the_query_industry_and_current_entity(self):
        response = self.client.post(
            self.list_url,
            self._payload(holder=self.other_entity.id),
            content_type="application/json",
            query_params=self.base_params,
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created = Action.objects.get(pk=response.data["id"])
        self.assertEqual(created.holder, self.entity)
        self.assertEqual(created.industry, Action.H2)

    def test_update_cannot_change_holder(self):
        response = self.client.patch(
            self._detail_url(self.own_action),
            {"holder": self.other_entity.id, "quantity": "42.000"},
            content_type="application/json",
            query_params=self.base_params,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.own_action.refresh_from_db()
        self.assertEqual(self.own_action.holder, self.entity)
        self.assertEqual(str(self.own_action.quantity), "42.000")

    def test_create_ignores_parent_id(self):
        response = self.client.post(
            self.list_url,
            self._payload(parent=self.own_action.id),
            content_type="application/json",
            query_params=self.base_params,
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created = Action.objects.get(pk=response.data["id"])
        self.assertIsNone(created.parent_id)

    def test_industry_query_param_is_required(self):
        response = self.client.get(self.list_url, {"entity_id": self.entity.id})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unknown_industry_query_param_is_rejected(self):
        response = self.client.get(
            self.list_url,
            {"entity_id": self.entity.id, "industry": "BIOMASS"},
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unauthenticated_request_is_rejected(self):
        self.client.logout()

        response = self.client.get(self.list_url, self.base_params)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
