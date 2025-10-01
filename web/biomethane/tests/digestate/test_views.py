from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from biomethane.factories import BiomethaneDigestateFactory, BiomethaneProductionUnitFactory
from biomethane.models.biomethane_digestate import BiomethaneDigestate
from biomethane.utils import get_declaration_period
from biomethane.views.digestate.digestate import BiomethaneDigestateViewSet
from core.models import Entity
from core.tests_utils import setup_current_user

User = get_user_model()


class BiomethaneDigestateViewsTests(TestCase):
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

        BiomethaneProductionUnitFactory.create(
            producer=self.producer_entity,
            has_digestate_phase_separation=False,
        )

        self.current_year = get_declaration_period()
        self.digestate_url = reverse("biomethane-digestate")
        self.base_params = {"entity_id": self.producer_entity.id, "year": self.current_year}

    @patch("biomethane.views.digestate.digestate.get_biomethane_permissions")
    def test_endpoints_permissions(self, mock_get_biomethane_permissions):
        """Test that the write actions are correctly defined"""
        viewset = BiomethaneDigestateViewSet()
        viewset.action = "retrieve"

        viewset.get_permissions()

        mock_get_biomethane_permissions.assert_called_once_with(["upsert", "validate_digestate"], "retrieve")

    def test_retrieve_digestate_success(self):
        """Test successful retrieval of digestate."""
        digestate = BiomethaneDigestateFactory.create(producer=self.producer_entity, year=self.current_year)

        response = self.client.get(self.digestate_url, self.base_params)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], digestate.id)
        self.assertEqual(response.data["producer"], self.producer_entity.id)
        self.assertEqual(response.data["year"], self.current_year)

    def test_retrieve_digestate_not_found(self):
        """Test retrieval when digestate doesn't exist."""
        response = self.client.get(self.digestate_url, self.base_params)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_digestate_success(self):
        """Test successful creation of digestate."""
        data = {
            "raw_digestate_tonnage_produced": 1500.0,
            "raw_digestate_dry_matter_rate": 8.5,
            "average_spreading_valorization_distance": 25.5,
        }

        response = self.client.put(self.digestate_url, data, content_type="application/json", query_params=self.base_params)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        digestate = BiomethaneDigestate.objects.get(producer=self.producer_entity, year=self.current_year)
        self.assertEqual(digestate.raw_digestate_tonnage_produced, data["raw_digestate_tonnage_produced"])
        self.assertEqual(digestate.raw_digestate_dry_matter_rate, data["raw_digestate_dry_matter_rate"])
        self.assertEqual(digestate.average_spreading_valorization_distance, data["average_spreading_valorization_distance"])

    def test_update_digestate_success(self):
        """Test successful update of digestate."""
        digestate = BiomethaneDigestateFactory.create(
            producer=self.producer_entity, year=self.current_year, raw_digestate_tonnage_produced=1000.0
        )

        data = {
            "raw_digestate_tonnage_produced": 2000.0,
            "raw_digestate_dry_matter_rate": 10.0,
            "average_spreading_valorization_distance": 50.0,
        }

        response = self.client.put(self.digestate_url, data, content_type="application/json", query_params=self.base_params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        digestate.refresh_from_db()
        self.assertEqual(digestate.raw_digestate_tonnage_produced, data["raw_digestate_tonnage_produced"])
        self.assertEqual(digestate.raw_digestate_dry_matter_rate, data["raw_digestate_dry_matter_rate"])

    def test_create_digestate_with_composting_validation_errors(self):
        """Test validation errors when composting data is incomplete."""
        data = {
            "raw_digestate_tonnage_produced": 1500.0,
            "composting_locations": [BiomethaneDigestate.EXTERNAL_PLATFORM],
            # Missing required fields for external platform
        }

        response = self.client.put(self.digestate_url, data, content_type="application/json", query_params=self.base_params)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
