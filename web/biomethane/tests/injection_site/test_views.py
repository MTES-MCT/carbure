from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from biomethane.factories.injection_site import BiomethaneInjectionSiteFactory
from biomethane.models import BiomethaneInjectionSite
from core.models import Entity
from core.tests_utils import setup_current_user

User = get_user_model()


class BiomethaneInjectionSiteViewsTests(TestCase):
    """Tests for biomethane injection site management views."""

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

        self.injection_site_url = reverse("biomethane-injection-site")

        self.base_params = {"entity_id": self.producer_entity.id}

    def test_retrieve_injection_site_success(self):
        """Test successful retrieval of injection site."""
        injection_site = BiomethaneInjectionSiteFactory.create(producer=self.producer_entity)

        response = self.client.get(self.injection_site_url, self.base_params)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], injection_site.id)
        self.assertEqual(response.data["producer"], self.producer_entity.id)
        self.assertEqual(response.data["unique_identification_number"], injection_site.unique_identification_number)

    def test_create_injection_site_success(self):
        """Test successful creation of injection site."""
        data = {
            "unique_identification_number": "INJ12345",
            "is_shared_injection_site": True,
            "meter_number": "METER123",
            "is_different_from_production_site": True,
            "company_address": "123 Test Street",
            "city": "Paris",
            "postal_code": "75001",
            "network_type": BiomethaneInjectionSite.TRANSPORT,
            "network_manager_name": "Test Network Manager",
        }

        response = self.client.put(
            self.injection_site_url, data, content_type="application/json", query_params=self.base_params
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        injection_site = BiomethaneInjectionSite.objects.get(producer=self.producer_entity)
        self.assertEqual(injection_site.unique_identification_number, data["unique_identification_number"])
        self.assertEqual(injection_site.meter_number, data["meter_number"])
        self.assertEqual(injection_site.company_address, data["company_address"])

    def test_update_injection_site_success(self):
        """Test successful update of injection site."""
        injection_site = BiomethaneInjectionSiteFactory.create(
            producer=self.producer_entity,
            meter_number="SHORT123",  # Specify a short meter_number to avoid factory issues
        )

        data = {
            "unique_identification_number": "INJ99999",
            "is_shared_injection_site": False,
            "is_different_from_production_site": False,
            "network_type": BiomethaneInjectionSite.DISTRIBUTION,
            "network_manager_name": "Updated Network Manager",
        }

        response = self.client.put(
            self.injection_site_url, data, content_type="application/json", query_params=self.base_params
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        injection_site.refresh_from_db()
        self.assertEqual(injection_site.unique_identification_number, data["unique_identification_number"])
        self.assertEqual(injection_site.network_type, data["network_type"])
        self.assertEqual(injection_site.network_manager_name, data["network_manager_name"])

    def test_create_injection_site_validation_errors(self):
        """Test validation errors during injection site creation."""
        data = {
            "unique_identification_number": "INJ12345",
            "is_shared_injection_site": True,  # meter_number required
            "is_different_from_production_site": True,  # address fields required
            # Missing: meter_number, company_address, city, postal_code
        }
        response = self.client.put(
            self.injection_site_url, data, content_type="application/json", query_params=self.base_params
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_injection_site_not_found(self):
        """Test 404 return when no injection site exists."""
        response = self.client.get(self.injection_site_url, self.base_params)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
