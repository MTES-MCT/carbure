from django.test import TestCase
from django.urls import reverse

from biomethane.factories import BiomethaneSupplyInputFactory, BiomethaneSupplyPlanFactory
from biomethane.services.annual_declaration import BiomethaneAnnualDeclarationService
from core.models import Entity, MatierePremiere
from core.tests_utils import setup_current_user


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

        self.matiere_mais = MatierePremiere.objects.create(
            name="Maïs",
            name_en="Corn",
            code="MAIS",
            is_methanogenic=True,
        )

        self.matiere_residus = MatierePremiere.objects.create(
            name="Résidus",
            name_en="Residues",
            code="RESIDUS",
            is_methanogenic=True,
        )

        self.supply_plan = BiomethaneSupplyPlanFactory.create(
            producer=self.producer_entity, year=BiomethaneAnnualDeclarationService.get_current_declaration_year()
        )

        self.supply_input = BiomethaneSupplyInputFactory.create(supply_plan=self.supply_plan)

        self.current_year = BiomethaneAnnualDeclarationService.get_current_declaration_year()
        self.url_base = reverse("biomethane-supply-input-list")
        self.base_params = {"entity_id": self.producer_entity.id, "year": self.current_year}

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
            "origin_country": "FR",
            "origin_department": "75",
            "average_weighted_distance_km": 50.0,
            "maximum_distance_km": 100.0,
            "volume": 500.0,
            "feedstock": "Maïs",
            "material_unit": "WET",
        }

        response = self.client.post(
            self.url_base, new_supply_data, content_type="application/json", query_params=self.base_params
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["feedstock"]["name"], "Maïs")
        self.assertEqual(response.data["origin_country"]["code_pays"], "FR")
        self.assertEqual(response.data["volume"], 500.0)

    def test_update_supply_input_success(self):
        """Test successful update of a supply input."""
        update_data = {
            "volume": 750.0,
            "feedstock": "Résidus",
        }

        response = self.client.patch(
            reverse("biomethane-supply-input-detail", args=[self.supply_input.id]),
            update_data,
            content_type="application/json",
            query_params=self.base_params,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["volume"], 750.0)
        self.assertEqual(response.data["feedstock"]["name"], "Résidus")

    def test_create_supply_input_invalid_data(self):
        """Test creation of a supply input with invalid data."""
        invalid_data = {}

        response = self.client.post(
            self.url_base, invalid_data, content_type="application/json", query_params=self.base_params
        )

        self.assertEqual(response.status_code, 400)
