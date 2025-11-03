from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from biomethane.models.biomethane_energy import BiomethaneEnergy
from biomethane.services.annual_declaration import BiomethaneAnnualDeclarationService
from biomethane.views.energy.energy import BiomethaneEnergyViewSet
from core.models import Entity
from core.tests_utils import assert_object_contains_data, setup_current_user


class BiomethaneEnergyViewSetTests(TestCase):
    def setUp(self):
        """Initial setup for tests"""
        self.viewset = BiomethaneEnergyViewSet()
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

        self.current_year = BiomethaneAnnualDeclarationService.get_declaration_period()
        self.energy_url = reverse("biomethane-energy")
        self.base_params = {"entity_id": self.producer_entity.id}

        # Test data for creating/updating an energy declaration
        self.valid_energy_data = {
            "injected_biomethane_gwh_pcs_per_year": 100.5,
            "injected_biomethane_nm3_per_year": 15000.0,
            "injected_biomethane_ch4_rate_percent": 95.0,
            "injected_biomethane_pcs_kwh_per_nm3": 10.5,
            "operating_hours": 8000.0,
        }

    @patch("biomethane.views.energy.energy.get_biomethane_permissions")
    def test_endpoints_permissions(self, mock_get_biomethane_permissions):
        """Test that the write actions are correctly defined"""
        viewset = BiomethaneEnergyViewSet()
        viewset.action = "retrieve"

        viewset.get_permissions()

        mock_get_biomethane_permissions.assert_called_once_with(["upsert", "validate_energy"], "retrieve")

    def test_retrieve_energy_success(self):
        """Test successful retrieval of an existing energy declaration"""
        # Create an energy declaration
        BiomethaneEnergy.objects.create(
            producer=self.producer_entity,
            year=self.current_year,
            **self.valid_energy_data,
        )
        params = {**self.base_params, "year": self.current_year}
        response = self.client.get(self.energy_url, params)

        self.assertEqual(response.data["year"], self.current_year)
        self.assertEqual(response.data["producer"], self.producer_entity.id)
        assert_object_contains_data(self, response.data, self.valid_energy_data)

    def test_retrieve_energy_not_found(self):
        """Test 404 return when no energy declaration exists"""
        params = {**self.base_params, "year": 1995}
        response = self.client.get(self.energy_url, params)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_upsert_create_energy_success(self):
        """Test successful creation of a new energy declaration"""
        response = self.client.put(
            self.energy_url,
            self.valid_energy_data,
            content_type="application/json",
            query_params=self.base_params,
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verify that the object was created in the database
        energy = BiomethaneEnergy.objects.get(producer=self.producer_entity, year=self.current_year)
        self.assertEqual(energy.year, self.current_year)
        assert_object_contains_data(self, energy, self.valid_energy_data)

    def test_upsert_update_energy_success(self):
        """Test successful update of an existing energy declaration"""
        # Create an existing energy declaration
        energy = BiomethaneEnergy.objects.create(
            producer=self.producer_entity,
            year=self.current_year,
            injected_biomethane_gwh_pcs_per_year=50.0,
        )
        # Update data
        update_data = {
            "injected_biomethane_gwh_pcs_per_year": 200.0,
            "operating_hours": 8500.0,
        }

        response = self.client.put(
            self.energy_url,
            update_data,
            content_type="application/json",
            query_params=self.base_params,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        energy.refresh_from_db()
        self.assertEqual(energy.injected_biomethane_gwh_pcs_per_year, 200.0)
        self.assertEqual(energy.operating_hours, 8500.0)
        self.assertEqual(energy.year, self.current_year)

    @patch(
        "biomethane.services.annual_declaration.BiomethaneAnnualDeclarationService.is_declaration_editable",
        return_value=False,
    )
    def test_upsert_energy_forbidden_when_declaration_not_editable(self, mock_is_editable):
        """Test that upsert is forbidden when the annual declaration is not editable"""
        response = self.client.put(
            self.energy_url,
            self.valid_energy_data,
            content_type="application/json",
            query_params=self.base_params,
        )

        mock_is_editable.assert_called_once_with(self.producer_entity, self.current_year)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("error", response.data)
