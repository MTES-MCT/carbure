from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from core.models import Entity
from core.tests_utils import setup_current_user
from traceability.factories import ActionFactory
from traceability.models import Action


class ActionViewsetQuerysetTest(TestCase):
    fixtures = ["json/countries.json"]

    def setUp(self):
        self.entity = Entity.objects.create(name="HRS", entity_type=Entity.HRS)
        self.other_entity = Entity.objects.create(name="Other HRS", entity_type=Entity.HRS)
        setup_current_user(self, "tester@carbure.local", "Tester", "password", [(self.entity, "RW")])

        self.list_url = reverse("traceability-action-list")
        self.base_params = {"entity_id": self.entity.id, "industry": Action.H2}

        self.own_action = ActionFactory.create(holder=self.entity, industry=Action.H2)
        self.other_holder_action = ActionFactory.create(holder=self.other_entity, industry=Action.H2)
        self.child_of_own_action = ActionFactory.create(
            holder=self.other_entity,
            industry=Action.H2,
            parent=self.own_action,
        )
        self.other_industry_action = ActionFactory.create(holder=self.entity, industry="BIOMASS")

    def test_industry_query_param_is_required(self):
        response = self.client.get(self.list_url, {"entity_id": self.entity.id})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unknown_industry_query_param_is_rejected(self):
        response = self.client.get(
            self.list_url,
            {"entity_id": self.entity.id, "industry": "BIOMASS"},
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_includes_actions_held_or_whose_parent_is_held(self):
        response = self.client.get(self.list_url, self.base_params)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.own_action.id, ids)
        self.assertIn(self.child_of_own_action.id, ids)
        self.assertNotIn(self.other_holder_action.id, ids)

    def test_list_excludes_actions_from_another_industry(self):
        response = self.client.get(self.list_url, self.base_params)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.own_action.id, ids)
        self.assertNotIn(self.other_industry_action.id, ids)

    def test_list_displays_quantity_in_mj_by_default(self):
        self.own_action.quantity = Decimal("14400000.000")
        self.own_action.save(update_fields=["quantity"])

        response = self.client.get(self.list_url, self.base_params)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        item = next(result for result in response.data["results"] if result["id"] == self.own_action.id)
        self.assertEqual(item["quantity"], "14400000.000")
        self.assertEqual(item["display_quantity"], "14400000.000")
        self.assertEqual(item["display_unit"], "MJ")

    def test_list_displays_quantity_in_the_requested_unit(self):
        self.own_action.quantity = Decimal("14400000.000")
        self.own_action.save(update_fields=["quantity"])

        response = self.client.get(self.list_url, {**self.base_params, "quantity_unit": "kg"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        item = next(result for result in response.data["results"] if result["id"] == self.own_action.id)
        self.assertEqual(item["quantity"], "14400000.000")
        self.assertEqual(item["display_quantity"], "120000.000")
        self.assertEqual(item["display_unit"], "kg")

    def test_unknown_quantity_unit_is_rejected(self):
        response = self.client.get(self.list_url, {**self.base_params, "quantity_unit": "MWh"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("quantity_unit", response.data)
