from django.test import TestCase

from biomethane.factories import BiomethaneDigestateFactory, BiomethaneProductionUnitFactory
from biomethane.factories.contract import BiomethaneContractFactory
from biomethane.services.digestate import BiomethaneDigestateService
from core.models import Entity


class BiomethaneDigestateServiceTests(TestCase):
    def setUp(self):
        self.producer_entity = Entity.objects.create(
            name="Test Producer",
            entity_type=Entity.BIOMETHANE_PRODUCER,
        )
        self.production_unit = BiomethaneProductionUnitFactory.create(producer=self.producer_entity)
        self.contract = BiomethaneContractFactory.create(producer=self.producer_entity)

    def test_get_fields_to_clear_with_phase_separation(self):
        """Test that raw digestate fields are cleared when phase separation is used."""
        digestate = BiomethaneDigestateFactory.create(
            producer=self.producer_entity,
        )

        # Configure production unit with phase separation
        self.production_unit.has_digestate_phase_separation = True
        self.production_unit.save()

        fields_to_clear = BiomethaneDigestateService.get_fields_to_clear(digestate)

        self.assertIsInstance(fields_to_clear, list)
        # When phase separation is True, raw digestate fields should be cleared
        self.assertIn("raw_digestate_tonnage_produced", fields_to_clear)
        self.assertIn("raw_digestate_dry_matter_rate", fields_to_clear)

    def test_get_fields_to_clear_without_phase_separation(self):
        """Test that separated digestate fields are cleared when no phase separation."""
        digestate = BiomethaneDigestateFactory.create(
            producer=self.producer_entity,
        )

        # Configure production unit without phase separation
        self.production_unit.has_digestate_phase_separation = False
        self.production_unit.save()

        fields_to_clear = BiomethaneDigestateService.get_fields_to_clear(digestate)

        # When phase separation is False, separated digestate fields should be cleared
        self.assertIn("solid_digestate_tonnage", fields_to_clear)
        self.assertIn("liquid_digestate_quantity", fields_to_clear)

    def test_get_fields_to_clear_when_no_composting(self):
        """Test that composting fields are cleared when composting is disabled."""
        digestate = BiomethaneDigestateFactory.create(
            producer=self.producer_entity,
        )

        fields_to_clear = BiomethaneDigestateService.get_fields_to_clear(digestate)

        self.assertIsInstance(fields_to_clear, list)

        # Composting-related fields should be in the clear list when not enabled
        self.assertIn("composting_locations", fields_to_clear)
        self.assertIn("external_platform_name", fields_to_clear)

    def test_get_optional_fields_returns_same_as_fields_to_clear(self):
        """Test that get_optional_fields returns the same list as get_fields_to_clear."""
        digestate = BiomethaneDigestateFactory.create(
            producer=self.producer_entity,
        )

        optional_fields = BiomethaneDigestateService.get_optional_fields(digestate)
        fields_to_clear = BiomethaneDigestateService.get_fields_to_clear(digestate)

        self.assertIsInstance(optional_fields, list)
        self.assertEqual(optional_fields, fields_to_clear)
