from django.test import TestCase

from biomethane.factories.injection_site import BiomethaneInjectionSiteFactory
from biomethane.models import BiomethaneInjectionSite
from core.models import Entity


class BiomethaneInjectionSiteSignalTests(TestCase):
    """Unit tests for BiomethaneInjectionSite signals."""

    def setUp(self):
        """Initial setup for signal tests."""
        self.producer_entity = Entity.objects.create(
            name="Test Producer",
            entity_type=Entity.BIOMETHANE_PRODUCER,
        )

        self.injection_site = BiomethaneInjectionSiteFactory.create(
            producer=self.producer_entity,
            is_shared_injection_site=True,
            meter_number="BASE_METER",
            is_different_from_production_site=True,
            company_address="123 Base Street",
            city="Base City",
            postal_code="12345",
            network_type=BiomethaneInjectionSite.TRANSPORT,
        )

    def test_clear_meter_number_when_not_shared_injection_site(self):
        """Test meter_number is cleared when is_shared_injection_site becomes False."""
        # Verify initial state (should have meter_number from setUp)
        self.assertEqual(self.injection_site.meter_number, "BASE_METER")
        self.assertTrue(self.injection_site.is_shared_injection_site)

        # Update to non-shared injection site
        self.injection_site.is_shared_injection_site = False
        self.injection_site.save()

        # Reload from database and verify meter_number is cleared
        self.injection_site.refresh_from_db()
        self.assertIsNone(self.injection_site.meter_number)
        self.assertFalse(self.injection_site.is_shared_injection_site)

    def test_clear_address_fields_when_same_as_production_site(self):
        """Test address fields are cleared when is_different_from_production_site becomes False."""
        # Verify initial state (should have address fields from setUp)
        self.assertEqual(self.injection_site.company_address, "123 Base Street")
        self.assertEqual(self.injection_site.city, "Base City")
        self.assertEqual(self.injection_site.postal_code, "12345")
        self.assertTrue(self.injection_site.is_different_from_production_site)

        # Update to same as production site
        self.injection_site.is_different_from_production_site = False
        self.injection_site.save()

        # Reload from database and verify address fields are cleared
        self.injection_site.refresh_from_db()
        self.assertIsNone(self.injection_site.company_address)
        self.assertIsNone(self.injection_site.city)
        self.assertIsNone(self.injection_site.postal_code)
        self.assertFalse(self.injection_site.is_different_from_production_site)

    def test_preserve_fields_when_conditions_remain_true(self):
        """Test fields are preserved when boolean conditions remain True."""
        # Verify initial state from setUp (both conditions are True)
        self.assertEqual(self.injection_site.meter_number, "BASE_METER")
        self.assertEqual(self.injection_site.company_address, "123 Base Street")
        self.assertEqual(self.injection_site.city, "Base City")
        self.assertEqual(self.injection_site.postal_code, "12345")
        self.assertEqual(self.injection_site.network_type, BiomethaneInjectionSite.TRANSPORT)

        # Update only network_type (other fields should remain)
        self.injection_site.network_type = BiomethaneInjectionSite.DISTRIBUTION
        self.injection_site.save()

        # Reload from database and verify dependent fields are preserved
        self.injection_site.refresh_from_db()
        self.assertEqual(self.injection_site.meter_number, "BASE_METER")
        self.assertEqual(self.injection_site.company_address, "123 Base Street")
        self.assertEqual(self.injection_site.city, "Base City")
        self.assertEqual(self.injection_site.postal_code, "12345")
        self.assertEqual(self.injection_site.network_type, BiomethaneInjectionSite.DISTRIBUTION)
