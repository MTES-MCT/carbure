from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.urls import reverse

from biomethane.factories import BiomethaneSupplyInputFactory, BiomethaneSupplyPlanFactory
from biomethane.factories.production_unit import BiomethaneProductionUnitFactory
from biomethane.services.annual_declaration import BiomethaneAnnualDeclarationService
from core.models import Department, Entity, ExternalAdminRights, MatierePremiere
from core.tests_utils import setup_current_user
from entity.models import EntityScope


def create_dreal(departments=None):
    if departments is None:
        departments = []

    dreal = Entity.objects.create(
        name="Test DREAL",
        entity_type=Entity.EXTERNAL_ADMIN,
    )
    ExternalAdminRights.objects.create(entity=dreal, right=ExternalAdminRights.DREAL)
    for department in departments:
        EntityScope.objects.create(
            entity=dreal, content_type=ContentType.objects.get_for_model(Department), object_id=department.id
        )

    return dreal


def create_supply_plan_and_inputs(producer, year, inputs_count=10):
    supply_plan = BiomethaneSupplyPlanFactory.create(producer=producer, year=year)

    supply_inputs = BiomethaneSupplyInputFactory.create_batch(inputs_count, supply_plan=supply_plan)

    return supply_inputs


class BiomethaneSupplyInputViewSetTests(TestCase):
    fixtures = ["json/countries.json"]

    def setUp(self):
        self.dept_01 = Department.objects.create(code_dept="01", name="Ain")
        self.dept_02 = Department.objects.create(code_dept="02", name="Aisne")
        self.dreal = create_dreal([self.dept_01])

        self.producer_entity = Entity.objects.create(
            name="Test Producer",
            entity_type=Entity.BIOMETHANE_PRODUCER,
        )

        self.producer_entity_2 = Entity.objects.create(
            name="Test Producer 2",
            entity_type=Entity.BIOMETHANE_PRODUCER,
        )

        self.producer_entity_3 = Entity.objects.create(
            name="Test Producer 3",
            entity_type=Entity.BIOMETHANE_PRODUCER,
        )

        BiomethaneProductionUnitFactory.create(producer=self.producer_entity_2, department=self.dept_01)
        BiomethaneProductionUnitFactory.create(producer=self.producer_entity_3, department=self.dept_02)

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
            "source": "INTERNAL",
            "origin_country": "FR",
            "origin_department": "75",
            "crop_type": "MAIN",
            "volume": 500.0,
            "input_name": "Maïs",
            "material_unit": "WET",
        }

        response = self.client.post(
            self.url_base, new_supply_data, content_type="application/json", query_params=self.base_params
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["input_name"]["name"], "Maïs")
        self.assertEqual(response.data["origin_country"]["code_pays"], "FR")
        self.assertEqual(response.data["volume"], 500.0)

    def test_update_supply_input_success(self):
        """Test successful update of a supply input."""
        update_data = {
            "volume": 750.0,
            "input_name": "Résidus",
        }

        response = self.client.patch(
            reverse("biomethane-supply-input-detail", args=[self.supply_input.id]),
            update_data,
            content_type="application/json",
            query_params=self.base_params,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["volume"], 750.0)
        self.assertEqual(response.data["input_name"]["name"], "Résidus")

    def test_create_supply_input_invalid_data(self):
        """Test creation of a supply input with invalid data."""
        invalid_data = {}

        response = self.client.post(
            self.url_base, invalid_data, content_type="application/json", query_params=self.base_params
        )

        self.assertEqual(response.status_code, 400)

    ### Tests for DREAL ###
    def test_list_supply_inputs_success_with_dreal(self):
        """Test successful retrieval of supply inputs with DREAL (only supply inputs from
        the department associated with the DREAL are returned)."""

        setup_current_user(
            self,
            "dreal@carbure.local",
            "DREAL",
            "gogogo",
            [(self.dreal, "ADMIN")],
        )
        supply_inputs_entity_2 = create_supply_plan_and_inputs(self.producer_entity_2, 2020)
        create_supply_plan_and_inputs(self.producer_entity_3, 2020)

        params = {"entity_id": self.dreal.id, "year": 2020}

        response = self.client.get(self.url_base, params)

        self.assertEqual(response.status_code, 200)
        # Only 10 inputs are returned because the DREAL has access to only one department
        self.assertEqual(len(response.data["results"]), 10)

        supply_input_ids = [input["id"] for input in response.data["results"]]
        expected_supply_input_ids = [input.id for input in supply_inputs_entity_2]

        self.assertEqual(supply_input_ids, expected_supply_input_ids)

    def test_list_supply_inputs_success_with_dreal_and_producer_id(self):
        """Test successful retrieval of supply inputs with DREAL and producer_id (in case of DREAL
        access to a specific entity)."""

        setup_current_user(
            self,
            "dreal@carbure.local",
            "DREAL",
            "gogogo",
            [(self.dreal, "ADMIN")],
        )
        supply_inputs_entity_2 = create_supply_plan_and_inputs(self.producer_entity_2, 2020)
        create_supply_plan_and_inputs(self.producer_entity_3, 2020)

        params = {"entity_id": self.dreal.id, "producer_id": self.producer_entity_2.id, "year": 2020}

        response = self.client.get(self.url_base, params)

        self.assertEqual(len(response.data["results"]), 10)

        supply_input_ids = [input["id"] for input in response.data["results"]]
        expected_supply_input_ids = [input.id for input in supply_inputs_entity_2]

        self.assertEqual(supply_input_ids, expected_supply_input_ids)

    def test_list_supply_inputs_error_with_dreal_and_not_allowed_producer_id(self):
        """Test error retrieval of supply inputs with DREAL and not allowed producer_id."""

        setup_current_user(
            self,
            "dreal@carbure.local",
            "DREAL",
            "gogogo",
            [(self.dreal, "ADMIN")],
        )
        create_supply_plan_and_inputs(self.producer_entity_3, 2020)

        params = {"entity_id": self.dreal.id, "producer_id": self.producer_entity_3.id, "year": 2020}

        response = self.client.get(self.url_base, params)

        self.assertEqual(response.status_code, 403)
