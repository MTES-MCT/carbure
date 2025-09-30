from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from biomethane.factories.digestate import BiomethaneDigestateFactory
from biomethane.factories.digestate_spreading import BiomethaneDigestateSpreadingFactory
from biomethane.models.biomethane_digestate_spreading import BiomethaneDigestateSpreading
from biomethane.views.digestate.spreading import BiomethaneDigestateSpreadingViewSet
from core.models import Entity
from core.tests_utils import setup_current_user


class BiomethaneDigestateSpreadingViewSetTests(TestCase):
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

        self.digestate = BiomethaneDigestateFactory.create(
            producer=self.producer_entity,
            average_spreading_valorization_distance=50.0,
        )

        self.url_base = reverse("biomethane-digestate-spreading-list")
        self.base_params = {"entity_id": self.producer_entity.id}

    @patch("biomethane.views.digestate.spreading.get_biomethane_permissions")
    def test_endpoints_permissions(self, mock_get_biomethane_permissions):
        """Test that the write actions are correctly defined"""
        viewset = BiomethaneDigestateSpreadingViewSet()
        viewset.action = "retrieve"

        viewset.get_permissions()

        mock_get_biomethane_permissions.assert_called_once_with(["create", "destroy"], "retrieve")

    def test_create_digestate_spreading_success(self):
        """Test successful creation of digestate spreading record."""
        create_data = {
            "spreading_department": "69",
            "spread_quantity": 150.0,
            "spread_parcels_area": 75.0,
        }

        response = self.client.post(self.url_base, create_data, query_params=self.base_params)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verify spreading was created
        created_spreading = BiomethaneDigestateSpreading.objects.get(digestate_id=self.digestate.id)
        self.assertEqual(created_spreading.digestate, self.digestate)
        self.assertEqual(created_spreading.spreading_department, "69")
        self.assertEqual(created_spreading.spread_quantity, 150.0)
        self.assertEqual(created_spreading.spread_parcels_area, 75.0)

    def test_delete_digestate_spreading_success(self):
        """Test successful deletion of spreading record."""
        spreading = BiomethaneDigestateSpreadingFactory.create(
            digestate=self.digestate,
            spreading_department="75",
            spread_quantity=100.0,
            spread_parcels_area=50.0,
        )

        # Get the detail URL for deletion
        url = reverse("biomethane-digestate-spreading-detail", kwargs={"pk": spreading.id})
        response = self.client.delete(url, query_params=self.base_params)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Verify spreading was deleted
        self.assertFalse(BiomethaneDigestateSpreading.objects.filter(id=spreading.id).exists())
