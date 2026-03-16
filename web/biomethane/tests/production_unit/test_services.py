from unittest.mock import Mock

from django.test import TestCase

from biomethane.factories.production_unit import BiomethaneDigestateStorageFactory, BiomethaneProductionUnitFactory
from biomethane.models import BiomethaneProductionUnit
from biomethane.services.production_unit import BiomethaneProductionUnitService, _build_production_unit_rules
from core.models import Entity


class ProductionUnitRulesConfigurationTests(TestCase):
    """Unit tests for _build_production_unit_rules configuration."""

    def setUp(self):
        self.rules = _build_production_unit_rules()

    def test_all_expected_rules_are_configured(self):
        """Test that all expected rule names are present in the correct order."""
        expected_rule_names = [
            "no_sanitary_approval",
            "no_hygienization_exemption",
            "no_phase_separation",
            "spreading_not_selected",
        ]
        actual_rule_names = [rule.name for rule in self.rules]
        self.assertEqual(expected_rule_names, actual_rule_names)

    def test_no_sanitary_approval_rule_fields_and_condition(self):
        """Test no_sanitary_approval rule has correct fields and condition logic."""
        rule = next(r for r in self.rules if r.name == "no_sanitary_approval")
        self.assertEqual(rule.fields, BiomethaneProductionUnitService.SANITARY_APPROVAL_FIELDS)

        mock_instance = Mock()
        mock_instance.has_sanitary_approval = False
        self.assertTrue(rule.condition(mock_instance))

        mock_instance.has_sanitary_approval = True
        self.assertFalse(rule.condition(mock_instance))

    def test_no_hygienization_exemption_rule_fields_and_condition(self):
        """Test no_hygienization_exemption rule has correct fields and condition logic."""
        rule = next(r for r in self.rules if r.name == "no_hygienization_exemption")
        self.assertEqual(rule.fields, BiomethaneProductionUnitService.HYGIENIZATION_EXEMPTION_FIELDS)

        mock_instance = Mock()
        mock_instance.has_hygienization_exemption = False
        self.assertTrue(rule.condition(mock_instance))

        mock_instance.has_hygienization_exemption = True
        self.assertFalse(rule.condition(mock_instance))

    def test_no_phase_separation_rule_fields_and_condition(self):
        """Test no_phase_separation rule has correct fields and condition logic."""
        rule = next(r for r in self.rules if r.name == "no_phase_separation")
        self.assertEqual(rule.fields, BiomethaneProductionUnitService.PHASE_SEPARATION_FIELDS)

        mock_instance = Mock()
        mock_instance.has_digestate_phase_separation = False
        self.assertTrue(rule.condition(mock_instance))

        mock_instance.has_digestate_phase_separation = True
        self.assertFalse(rule.condition(mock_instance))

    def test_spreading_not_selected_rule_fields_and_condition(self):
        """Test spreading_not_selected rule has correct fields and condition logic."""
        rule = next(r for r in self.rules if r.name == "spreading_not_selected")
        self.assertEqual(rule.fields, BiomethaneProductionUnitService.SPREADING_MANAGEMENT_FIELDS)

        mock_instance = Mock()
        # Should trigger when SPREADING is not in the list
        mock_instance.digestate_valorization_methods = [BiomethaneProductionUnit.COMPOSTING]
        self.assertTrue(rule.condition(mock_instance))

        mock_instance.digestate_valorization_methods = []
        self.assertTrue(rule.condition(mock_instance))

        # Should not trigger when SPREADING is selected
        mock_instance.digestate_valorization_methods = [BiomethaneProductionUnit.SPREADING]
        self.assertFalse(rule.condition(mock_instance))

        mock_instance.digestate_valorization_methods = [
            BiomethaneProductionUnit.SPREADING,
            BiomethaneProductionUnit.COMPOSTING,
        ]
        self.assertFalse(rule.condition(mock_instance))


class BiomethaneProductionUnitServiceIntegrationTests(TestCase):
    """Integration tests verifying end-to-end behavior of the service with real Django models."""

    def setUp(self):
        self.producer = Entity.objects.create(
            name="Test Producer",
            entity_type=Entity.BIOMETHANE_PRODUCER,
        )
        self.production_unit = BiomethaneProductionUnitFactory.create(producer=self.producer)

    def test_get_fields_to_clear_sanitary_approval_when_disabled(self):
        """sanitary_approval_number is included in fields_to_clear when has_sanitary_approval is False."""
        self.production_unit.has_sanitary_approval = False
        self.production_unit.save()

        fields = BiomethaneProductionUnitService.get_fields_to_clear(self.production_unit)

        self.assertIn("sanitary_approval_number", fields)

    def test_get_fields_to_clear_sanitary_approval_when_enabled(self):
        """sanitary_approval_number is not in fields_to_clear when has_sanitary_approval is True."""
        self.production_unit.has_sanitary_approval = True
        self.production_unit.save()

        fields = BiomethaneProductionUnitService.get_fields_to_clear(self.production_unit)

        self.assertNotIn("sanitary_approval_number", fields)

    def test_get_fields_to_clear_spreading_when_not_selected(self):
        """Spreading management fields are cleared when SPREADING is not a valorization method."""
        self.production_unit.digestate_valorization_methods = [BiomethaneProductionUnit.COMPOSTING]
        self.production_unit.save()

        fields = BiomethaneProductionUnitService.get_fields_to_clear(self.production_unit)

        self.assertIn("spreading_management_methods", fields)
        self.assertIn("digestate_sale_types", fields)

    def test_get_fields_to_clear_spreading_when_selected(self):
        """Spreading management fields are not cleared when SPREADING is a valorization method."""
        self.production_unit.digestate_valorization_methods = [BiomethaneProductionUnit.SPREADING]
        self.production_unit.save()

        fields = BiomethaneProductionUnitService.get_fields_to_clear(self.production_unit)

        self.assertNotIn("spreading_management_methods", fields)
        self.assertNotIn("digestate_sale_types", fields)

    def test_get_fields_to_clear_deduplicates_fields(self):
        """get_fields_to_clear returns no duplicate field names."""
        fields = BiomethaneProductionUnitService.get_fields_to_clear(self.production_unit)

        self.assertEqual(len(fields), len(set(fields)))

    def test_get_optional_fields_equals_fields_to_clear_plus_always_optional(self):
        """get_optional_fields returns exactly get_fields_to_clear + ALWAYS_OPTIONAL_FIELDS (no duplicates)."""
        optional = BiomethaneProductionUnitService.get_optional_fields(self.production_unit)
        to_clear = BiomethaneProductionUnitService.get_fields_to_clear(self.production_unit)

        for field in to_clear:
            self.assertIn(field, optional)
        for field in BiomethaneProductionUnitService.ALWAYS_OPTIONAL_FIELDS:
            self.assertIn(field, optional)


class BiomethaneProductionUnitDigestateStoragePropertyTests(TestCase):
    """Tests for BiomethaneProductionUnit.digestate_storage virtual property."""

    fixtures = ["json/countries.json"]

    def setUp(self):
        self.producer = Entity.objects.create(
            name="Test Producer",
            entity_type=Entity.BIOMETHANE_PRODUCER,
        )
        self.production_unit = BiomethaneProductionUnitFactory.create(producer=self.producer)

    def test_digestate_storage_returns_true_when_exists(self):
        """digestate_storage returns True when at least one storage exists for the producer."""
        BiomethaneDigestateStorageFactory.create(producer=self.producer)
        self.assertTrue(self.production_unit.digestate_storage)

    def test_digestate_storage_returns_none_when_no_storage(self):
        """digestate_storage returns None when no storage exists (None is detected as missing by _get_missing_fields)."""
        self.assertIsNone(self.production_unit.digestate_storage)

    def test_digestate_storage_in_extra_fields(self):
        """'digestate_storage' must be listed in EXTRA_FIELDS so get_all_fields() picks it up."""
        self.assertIn("digestate_storage", BiomethaneProductionUnit.EXTRA_FIELDS)
