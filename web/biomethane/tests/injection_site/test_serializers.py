from django.test import TestCase

from biomethane.models import BiomethaneInjectionSite
from biomethane.serializers import BiomethaneInjectionSiteInputSerializer
from core.models import Entity


class BiomethaneInjectionSiteSerializerTests(TestCase):
    """Unit tests for BiomethaneInjectionSite serializers."""

    def setUp(self):
        """Initial setup for serializer validation tests."""
        self.producer_entity = Entity.objects.create(
            name="Test Producer",
            entity_type=Entity.BIOMETHANE_PRODUCER,
        )

        self.context = {"entity": self.producer_entity}

        self.producer_entity2 = Entity.objects.create(
            name="Test Producer 2",
            entity_type=Entity.BIOMETHANE_PRODUCER,
        )

    def test_injection_site_input_serializer_valid_data(self):
        """Test creating injection site with valid data."""
        data = {
            "unique_identification_number": "NEW123",
            "is_shared_injection_site": True,
            "meter_number": "METER456",
            "is_different_from_production_site": True,
            "company_address": "456 New Street",
            "city": "Lyon",
            "postal_code": "69001",
            "network_type": BiomethaneInjectionSite.DISTRIBUTION,
            "network_manager_name": "New Manager",
        }

        serializer = BiomethaneInjectionSiteInputSerializer(data=data, context=self.context)
        self.assertTrue(serializer.is_valid())

    def test_injection_site_input_serializer_missing_base_fields(self):
        """Test validation error when base required fields are missing."""
        data = {
            # Missing: network_type, network_manager_name, unique_identification_number
        }

        serializer = BiomethaneInjectionSiteInputSerializer(data=data, context=self.context)
        self.assertFalse(serializer.is_valid())
        self.assertIn("network_type", serializer.errors)
        self.assertIn("network_manager_name", serializer.errors)
        self.assertIn("unique_identification_number", serializer.errors)

    def test_injection_site_input_serializer_missing_meter_number(self):
        """Test validation error when meter_number is missing for shared injection site."""
        data = {
            "unique_identification_number": "NEW123",
            "network_type": BiomethaneInjectionSite.TRANSPORT,
            "network_manager_name": "Test Manager",
            "is_shared_injection_site": True,  # meter_number required
            # Missing: meter_number
        }

        serializer = BiomethaneInjectionSiteInputSerializer(data=data, context=self.context)
        self.assertFalse(serializer.is_valid())
        self.assertIn("meter_number", serializer.errors)

    def test_injection_site_input_serializer_missing_address_fields(self):
        """Test validation error when address fields are missing for different production site."""
        data = {
            "unique_identification_number": "NEW123",
            "network_type": BiomethaneInjectionSite.TRANSPORT,
            "network_manager_name": "Test Manager",
            "is_different_from_production_site": True,  # address fields required
            # Missing: company_address, city, postal_code
        }

        serializer = BiomethaneInjectionSiteInputSerializer(data=data, context=self.context)
        self.assertFalse(serializer.is_valid())
        self.assertIn("company_address", serializer.errors)
        self.assertIn("city", serializer.errors)
        self.assertIn("postal_code", serializer.errors)

    def test_injection_site_input_serializer_invalid_network_type(self):
        """Test validation error for invalid network type."""
        data = {
            "unique_identification_number": "NEW123",
            "network_manager_name": "Test Manager",
            "network_type": "INVALID_TYPE",
        }

        serializer = BiomethaneInjectionSiteInputSerializer(data=data, context=self.context)
        self.assertFalse(serializer.is_valid())
        self.assertIn("network_type", serializer.errors)
