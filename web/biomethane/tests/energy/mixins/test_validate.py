from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from biomethane.models.biomethane_energy import BiomethaneEnergy
from biomethane.utils import get_declaration_period
from core.models import Entity
from core.tests_utils import setup_current_user


class ValidateActionMixinTests(TestCase):
    def setUp(self):
        """Initial setup for tests"""
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

        self.current_year = get_declaration_period()
        self.validate_url = reverse("biomethane-energy-validate")
        self.base_params = {"entity_id": self.producer_entity.id}

    def test_validate_energy_success(self):
        """Test successful validation of an energy declaration"""
        energy = BiomethaneEnergy.objects.create(
            producer=self.producer_entity,
            year=self.current_year,
            status=BiomethaneEnergy.PENDING,
            injected_biomethane_gwh_pcs_per_year=100.5,
        )

        response = self.client.post(
            self.validate_url,
            query_params=self.base_params,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        energy.refresh_from_db()
        self.assertEqual(energy.status, BiomethaneEnergy.VALIDATED)

    def test_validate_energy_not_found(self):
        """Test validation when no energy declaration exists"""
        response = self.client.post(
            self.validate_url,
            query_params=self.base_params,
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_validate_energy_different_year(self):
        """Test validation with a declaration from a different year"""
        different_year = 2023

        BiomethaneEnergy.objects.create(
            producer=self.producer_entity,
            year=different_year,
            status=BiomethaneEnergy.PENDING,
        )

        response = self.client.post(
            self.validate_url,
            query_params=self.base_params,
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
