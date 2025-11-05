from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from biomethane.factories import BiomethaneSupplyInputFactory, BiomethaneSupplyPlanFactory
from biomethane.services.annual_declaration import BiomethaneAnnualDeclarationService
from biomethane.views import BiomethaneSupplyInputViewSet
from core.models import Entity
from core.tests_utils import assert_object_contains_data, setup_current_user


class BiomethaneSupplyInputViewSetTests(TestCase):
    fixtures = ["json/countries.json"]

    def setUp(self):
        self.producer_entity = Entity.objects.create(
            name="Test Producer",
            entity_type=Entity.BIOMETHANE_PRODUCER,
        )

        self.user = setup_current_user(
            self,
            "tester@carbure.local",
            "Tester",
            "gogogo",
            [(self.producer_entity, "RW")],
        )

        self.supply_plan = BiomethaneSupplyPlanFactory.create(
            producer=self.producer_entity, year=BiomethaneAnnualDeclarationService.get_declaration_period()
        )

        self.supply_input = BiomethaneSupplyInputFactory.create(supply_plan=self.supply_plan)

        self.current_year = BiomethaneAnnualDeclarationService.get_declaration_period()
        self.url_base = reverse("biomethane-supply-input-list")
        self.base_params = {"entity_id": self.producer_entity.id, "year": self.current_year}

    @patch("biomethane.views.supply_plan.supply_input.get_biomethane_permissions")
    def test_endpoints_permissions(self, mock_get_biomethane_permissions):
        """Test that the write actions are correctly defined"""
        viewset = BiomethaneSupplyInputViewSet()
        viewset.action = "retrieve"

        viewset.get_permissions()

        mock_get_biomethane_permissions.assert_called_once_with(["create", "update", "partial_update"], "retrieve")

    def test_list_supply_inputs_success(self):
        """Test successful retrieval of supply inputs."""
        params = {**self.base_params, "year": 2020}

        response = self.client.get(self.url_base, params)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 0)

    def test_list_supply_inputs_success_with_no_supply_plan(self):
        """Test successful retrieval of supply inputs when no existing supply plan"""

        response = self.client.get(self.url_base, self.base_params)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)

    def test_create_supply_input_success(self):
        """Test successful creation of a supply input."""
        new_supply_data = {
            "supply_plan": self.supply_plan.id,
            "source": "INTERNAL",
            "origin_country": "FR",
            "origin_department": "75",
            "crop_type": "MAIN",
            "volume": 500.0,
            "input_category": "CIVE",
            "input_type": "Maïs",
            "material_unit": "WET",
        }

        response = self.client.post(
            self.url_base, new_supply_data, content_type="application/json", query_params=self.base_params
        )

        expected_data = {
            **new_supply_data,
            "origin_country": {"name": "France", "name_en": "France", "code_pays": "FR", "is_in_europe": True},
        }

        self.assertEqual(response.status_code, 201)
        assert_object_contains_data(self, response.data, expected_data, object_name="supply input")

    def test_update_supply_input_success(self):
        """Test successful update of a supply input."""
        update_data = {
            "volume": 750.0,
            "input_type": "Résidus",
        }

        response = self.client.patch(
            reverse("biomethane-supply-input-detail", args=[self.supply_input.id]),
            update_data,
            content_type="application/json",
            query_params=self.base_params,
        )

        self.assertEqual(response.status_code, 200)
        assert_object_contains_data(self, response.data, update_data, object_name="supply input")

    def test_create_supply_input_invalid_data(self):
        """Test creation of a supply input with invalid data."""
        invalid_data = {}

        response = self.client.post(
            self.url_base, invalid_data, content_type="application/json", query_params=self.base_params
        )

        self.assertEqual(response.status_code, 400)
