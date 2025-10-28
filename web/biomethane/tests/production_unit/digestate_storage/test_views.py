from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from biomethane.models import BiomethaneDigestateStorage
from biomethane.views.production_unit.digestate_storage import BiomethaneDigestateStorageViewSet
from core.models import Entity
from core.tests_utils import setup_current_user


class BiomethaneDigestateStorageViewsTests(TestCase):
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

        self.digestate_storage_url = reverse("biomethane-digestate-storage-list")
        self.base_params = {"entity_id": self.producer_entity.id}

    @patch("biomethane.views.production_unit.digestate_storage.get_biomethane_permissions")
    def test_endpoints_permissions(self, mock_get_biomethane_permissions):
        """Test that the write actions are correctly defined"""
        viewset = BiomethaneDigestateStorageViewSet()
        viewset.action = "list"

        viewset.get_permissions()

        mock_get_biomethane_permissions.assert_called_once_with(["create", "destroy", "destoy", "partial_update"], "list")

    def test_list_digestate_storages(self):
        """Test listing all digestate storages for a producer."""
        # Create some storages
        BiomethaneDigestateStorage.objects.create(
            producer=self.producer_entity,
            type="LAGOON",
            capacity=5000.0,
            has_cover=True,
            has_biogas_recovery=True,
        )
        BiomethaneDigestateStorage.objects.create(
            producer=self.producer_entity,
            type="TANK",
            capacity=3000.0,
            has_cover=False,
            has_biogas_recovery=False,
        )

        response = self.client.get(self.digestate_storage_url, self.base_params)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_create_digestate_storage(self):
        """Test creating a new digestate storage."""
        data = {
            "type": "LAGOON",
            "capacity": 4500.0,
            "has_cover": True,
            "has_biogas_recovery": False,
        }

        response = self.client.post(
            self.digestate_storage_url, data, content_type="application/json", query_params=self.base_params
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verify it was created in database
        storage = BiomethaneDigestateStorage.objects.get(producer=self.producer_entity)
        self.assertEqual(storage.type, "LAGOON")
        self.assertEqual(storage.capacity, 4500.0)
        self.assertTrue(storage.has_cover)
        self.assertFalse(storage.has_biogas_recovery)

    def test_update_digestate_storage(self):
        """Test updating an existing digestate storage."""
        storage = BiomethaneDigestateStorage.objects.create(
            producer=self.producer_entity,
            type="LAGOON",
            capacity=5000.0,
            has_cover=False,
            has_biogas_recovery=False,
        )

        update_data = {
            "type": "LAGOON",
            "capacity": 6000.0,
            "has_cover": True,
            "has_biogas_recovery": True,
        }

        detail_url = reverse("biomethane-digestate-storage-detail", kwargs={"pk": storage.pk})
        response = self.client.put(detail_url, update_data, content_type="application/json", query_params=self.base_params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify it was updated
        storage.refresh_from_db()
        self.assertEqual(storage.capacity, 6000.0)
        self.assertTrue(storage.has_cover)
        self.assertTrue(storage.has_biogas_recovery)

    def test_delete_digestate_storage(self):
        """Test deleting a digestate storage."""
        storage = BiomethaneDigestateStorage.objects.create(
            producer=self.producer_entity,
            type="TANK",
            capacity=3000.0,
            has_cover=False,
            has_biogas_recovery=False,
        )

        detail_url = reverse("biomethane-digestate-storage-detail", kwargs={"pk": storage.pk})
        response = self.client.delete(detail_url, query_params=self.base_params)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Verify it was deleted
        self.assertEqual(BiomethaneDigestateStorage.objects.filter(producer=self.producer_entity).count(), 0)

    def test_list_only_shows_producer_storages(self):
        """Test that list endpoint only returns storages for the authenticated producer."""
        # Create storage for this producer
        BiomethaneDigestateStorage.objects.create(
            producer=self.producer_entity,
            type="LAGOON",
            capacity=5000.0,
            has_cover=True,
            has_biogas_recovery=True,
        )

        # Create storage for another producer
        other_producer = Entity.objects.create(
            name="Other Producer",
            entity_type=Entity.BIOMETHANE_PRODUCER,
        )
        BiomethaneDigestateStorage.objects.create(
            producer=other_producer,
            type="TANK",
            capacity=3000.0,
            has_cover=False,
            has_biogas_recovery=False,
        )

        response = self.client.get(self.digestate_storage_url, self.base_params)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should only see own storage
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["type"], "LAGOON")
