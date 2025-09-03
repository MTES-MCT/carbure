from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from biomethane.models import BiomethaneInjectionSite
from core.models import Entity
from core.tests_utils import assert_object_contains_data, setup_current_user


class BiomethaneInjectionSiteTests(TestCase):
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
        self.injection_site_url += "?entity_id=" + str(self.producer_entity.id)

        self.valid_data = {
            "unique_identification_number": "1234567890",
            "is_shared_injection_site": True,
            "meter_number": "1234567890",
            "is_different_from_production_site": True,
            "company_address": "1234567890",
            "city": "Paris",
            "postal_code": "75000",
        }

    def test_permission_boundary(self):
        # Create non-biomethane producer entity
        wrong_entity = Entity.objects.create(
            name="Wrong Entity",
            entity_type=Entity.OPERATOR,
        )

        setup_current_user(
            self,
            "wrong@carbure.local",
            "Wrong User",
            "gogogo2",
            [(wrong_entity, "RW")],
        )

        wrong_url = reverse("biomethane-injection-site")
        wrong_url += "?entity_id=" + str(wrong_entity.id)

        response = self.client.get(wrong_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_errors_in_create_injection_site(self):
        response = self.client.put(
            self.injection_site_url,
            {
                "unique_identification_number": "1234567890",
                "is_shared_injection_site": True,
                "is_different_from_production_site": True,
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("meter_number", response.data)
        self.assertIn("company_address", response.data)
        self.assertIn("city", response.data)
        self.assertIn("postal_code", response.data)

    def test_create_injection_site(self):
        response = self.client.put(
            self.injection_site_url,
            self.valid_data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        injection_site = BiomethaneInjectionSite.objects.get(entity=self.producer_entity)

        assert_object_contains_data(self, injection_site, self.valid_data)

    def test_update_injection_site(self):
        # Create injection site
        response = self.client.put(
            self.injection_site_url,
            self.valid_data,
            content_type="application/json",
        )

        updated_data = {
            "unique_identification_number": "999",
            "is_shared_injection_site": False,
            "is_different_from_production_site": False,
        }

        # Update injection site and check meter_number / company_address / city / postal_code are reseted
        response = self.client.put(
            self.injection_site_url,
            updated_data,
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        injection_site = BiomethaneInjectionSite.objects.get(entity=self.producer_entity)
        assert_object_contains_data(self, injection_site, updated_data)

        for field in ["meter_number", "company_address", "city", "postal_code"]:
            self.assertIsNone(getattr(injection_site, field))
