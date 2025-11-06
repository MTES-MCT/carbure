from django.test import TestCase

from biomethane.factories import BiomethaneDigestateFactory, BiomethaneProductionUnitFactory
from biomethane.factories.contract import BiomethaneContractFactory
from biomethane.models import BiomethaneContract, BiomethaneDigestate, BiomethaneProductionUnit
from biomethane.services.digestate import BiomethaneDigestateService, DigestateContext, _build_digestate_rules
from core.models import Entity


class DigestateContextExtractionTests(TestCase):
    """Test the _extract_data method that builds DigestateContext."""

    def setUp(self):
        self.producer_entity = Entity.objects.create(
            name="Test Producer",
            entity_type=Entity.BIOMETHANE_PRODUCER,
        )

    def test_extract_data_with_full_context(self):
        """Test context extraction when all related objects exist."""
        production_unit = BiomethaneProductionUnitFactory.create(producer=self.producer_entity)
        contract = BiomethaneContractFactory.create(producer=self.producer_entity)
        digestate = BiomethaneDigestateFactory.create(producer=self.producer_entity)

        context = BiomethaneDigestateService._extract_data(digestate)

        self.assertIsInstance(context, DigestateContext)
        self.assertEqual(context.instance, digestate)
        self.assertEqual(context.production_unit, production_unit)
        self.assertEqual(context.contract, contract)

    def test_extract_data_without_production_unit(self):
        """Test context extraction when production_unit doesn't exist."""
        digestate = BiomethaneDigestateFactory.create(producer=self.producer_entity)

        context = BiomethaneDigestateService._extract_data(digestate)

        self.assertIsNone(context.production_unit)

    def test_extract_data_without_contract(self):
        """Test context extraction when contract doesn't exist."""
        digestate = BiomethaneDigestateFactory.create(producer=self.producer_entity)

        context = BiomethaneDigestateService._extract_data(digestate)

        self.assertIsNone(context.contract)

    def test_composting_locations_property_returns_list(self):
        """Test that composting_locations property always returns a list."""
        digestate = BiomethaneDigestateFactory.create(
            producer=self.producer_entity,
            composting_locations=[BiomethaneDigestate.ON_SITE],
        )

        context = BiomethaneDigestateService._extract_data(digestate)

        self.assertIsInstance(context.composting_locations, list)
        self.assertEqual(context.composting_locations, [BiomethaneDigestate.ON_SITE])

    def test_composting_locations_property_handles_none(self):
        """Test that composting_locations property returns empty list when empty."""
        digestate = BiomethaneDigestateFactory.create(
            producer=self.producer_entity,
            composting_locations=[],
        )

        context = BiomethaneDigestateService._extract_data(digestate)

        self.assertEqual(context.composting_locations, [])


class DigestateRulesConfigurationTests(TestCase):
    """Test the _build_digestate_rules function configuration."""

    def setUp(self):
        self.rules = _build_digestate_rules()

    def test_all_expected_rules_are_configured(self):
        """Test that all expected rule names are present in the configuration."""
        expected_rule_names = [
            "phase_separation_enabled",
            "phase_separation_disabled",
            "spreading_not_selected",
            "incineration_not_selected",
            "composting_disabled",
            "external_platform_not_selected",
            "on_site_not_selected",
            "sale_not_selected",
            "wwtp_category_not_2",
        ]

        actual_rule_names = [rule.name for rule in self.rules]
        self.assertEqual(expected_rule_names, actual_rule_names)

    def test_phase_separation_enabled_rule_fields_and_condition(self):
        """Test phase separation enabled rule has correct fields and condition logic."""
        from unittest.mock import Mock

        phase_sep_enabled_rule = next(r for r in self.rules if r.name == "phase_separation_enabled")
        self.assertEqual(phase_sep_enabled_rule.fields, BiomethaneDigestateService.RAW_DIGESTATE_FIELDS)

        # Should trigger when phase separation is enabled
        mock_ctx = Mock()
        mock_ctx.production_unit = Mock()
        mock_ctx.production_unit.has_digestate_phase_separation = True
        self.assertTrue(phase_sep_enabled_rule.condition(mock_ctx))

        # Should not trigger when phase separation is disabled
        mock_ctx.production_unit.has_digestate_phase_separation = False
        self.assertFalse(phase_sep_enabled_rule.condition(mock_ctx))

        # Should not trigger when no production unit
        mock_ctx.production_unit = None
        self.assertFalse(phase_sep_enabled_rule.condition(mock_ctx))

    def test_phase_separation_disabled_rule_fields_and_condition(self):
        """Test phase separation disabled rule has correct fields and condition logic."""
        from unittest.mock import Mock

        phase_sep_disabled_rule = next(r for r in self.rules if r.name == "phase_separation_disabled")
        self.assertEqual(phase_sep_disabled_rule.fields, BiomethaneDigestateService.SEPARATED_DIGESTATE_FIELDS)

        # Should trigger when phase separation is disabled
        mock_ctx = Mock()
        mock_ctx.production_unit = Mock()
        mock_ctx.production_unit.has_digestate_phase_separation = False
        self.assertTrue(phase_sep_disabled_rule.condition(mock_ctx))

        # Should not trigger when phase separation is enabled
        mock_ctx.production_unit.has_digestate_phase_separation = True
        self.assertFalse(phase_sep_disabled_rule.condition(mock_ctx))

        # Should not trigger when no production unit
        mock_ctx.production_unit = None
        self.assertFalse(phase_sep_disabled_rule.condition(mock_ctx))

    def test_spreading_not_selected_rule_fields_and_condition(self):
        """Test spreading rule has correct fields and condition logic."""
        from unittest.mock import Mock

        spreading_rule = next(r for r in self.rules if r.name == "spreading_not_selected")
        self.assertEqual(spreading_rule.fields, BiomethaneDigestateService.SPREADING_FIELDS)

        # Should trigger when SPREADING not in valorization methods
        mock_ctx = Mock()
        mock_ctx.production_unit = Mock()
        mock_ctx.production_unit.digestate_valorization_methods = [BiomethaneProductionUnit.COMPOSTING]
        self.assertTrue(spreading_rule.condition(mock_ctx))

        # Should not trigger when SPREADING is in valorization methods
        mock_ctx.production_unit.digestate_valorization_methods = [BiomethaneProductionUnit.SPREADING]
        self.assertFalse(spreading_rule.condition(mock_ctx))

    def test_incineration_not_selected_rule_fields_and_condition(self):
        """Test incineration rule has correct fields and condition logic."""
        from unittest.mock import Mock

        incineration_rule = next(r for r in self.rules if r.name == "incineration_not_selected")
        expected_fields = BiomethaneDigestateService.INCINERATION_FIELDS + BiomethaneDigestateService.WWTP_FIELDS
        self.assertEqual(incineration_rule.fields, expected_fields)

        # Should trigger when INCINERATION_LANDFILLING not in valorization methods
        mock_ctx = Mock()
        mock_ctx.production_unit = Mock()
        mock_ctx.production_unit.digestate_valorization_methods = [BiomethaneProductionUnit.SPREADING]
        self.assertTrue(incineration_rule.condition(mock_ctx))

        # Should not trigger when INCINERATION_LANDFILLING is in valorization methods
        mock_ctx.production_unit.digestate_valorization_methods = [BiomethaneProductionUnit.INCINERATION_LANDFILLING]
        self.assertFalse(incineration_rule.condition(mock_ctx))

    def test_composting_disabled_rule_fields_and_condition(self):
        """Test composting disabled rule has correct fields and condition logic."""
        from unittest.mock import Mock

        composting_disabled_rule = next(r for r in self.rules if r.name == "composting_disabled")
        expected_fields = (
            BiomethaneDigestateService.EXTERNAL_PLATFORM_FIELDS
            + BiomethaneDigestateService.ON_SITE_FIELDS
            + ["composting_locations"]
        )
        self.assertEqual(composting_disabled_rule.fields, expected_fields)

        # Should trigger when COMPOSTING not in valorization methods
        mock_ctx = Mock()
        mock_ctx.production_unit = Mock()
        mock_ctx.production_unit.digestate_valorization_methods = [BiomethaneProductionUnit.SPREADING]
        self.assertTrue(composting_disabled_rule.condition(mock_ctx))

        # Should not trigger when COMPOSTING is in valorization methods
        mock_ctx.production_unit.digestate_valorization_methods = [BiomethaneProductionUnit.COMPOSTING]
        self.assertFalse(composting_disabled_rule.condition(mock_ctx))

    def test_external_platform_not_selected_rule_fields_and_condition(self):
        """Test external platform rule has correct fields and condition logic."""
        from unittest.mock import Mock

        external_platform_rule = next(r for r in self.rules if r.name == "external_platform_not_selected")
        self.assertEqual(external_platform_rule.fields, BiomethaneDigestateService.EXTERNAL_PLATFORM_FIELDS)

        # Should trigger when COMPOSTING enabled but EXTERNAL_PLATFORM not in locations
        mock_ctx = Mock()
        mock_ctx.production_unit = Mock()
        mock_ctx.production_unit.digestate_valorization_methods = [BiomethaneProductionUnit.COMPOSTING]
        mock_ctx.composting_locations = [BiomethaneDigestate.ON_SITE]
        self.assertTrue(external_platform_rule.condition(mock_ctx))

        # Should not trigger when EXTERNAL_PLATFORM is in locations
        mock_ctx.composting_locations = [BiomethaneDigestate.EXTERNAL_PLATFORM]
        self.assertFalse(external_platform_rule.condition(mock_ctx))

        # Should not trigger when COMPOSTING not enabled
        mock_ctx.production_unit.digestate_valorization_methods = [BiomethaneProductionUnit.SPREADING]
        self.assertFalse(external_platform_rule.condition(mock_ctx))

    def test_on_site_not_selected_rule_fields_and_condition(self):
        """Test on-site rule has correct fields and condition logic."""
        from unittest.mock import Mock

        on_site_rule = next(r for r in self.rules if r.name == "on_site_not_selected")
        self.assertEqual(on_site_rule.fields, BiomethaneDigestateService.ON_SITE_FIELDS)

        # Should trigger when COMPOSTING enabled but ON_SITE not in locations
        mock_ctx = Mock()
        mock_ctx.production_unit = Mock()
        mock_ctx.production_unit.digestate_valorization_methods = [BiomethaneProductionUnit.COMPOSTING]
        mock_ctx.composting_locations = [BiomethaneDigestate.EXTERNAL_PLATFORM]
        self.assertTrue(on_site_rule.condition(mock_ctx))

        # Should not trigger when ON_SITE is in locations
        mock_ctx.composting_locations = [BiomethaneDigestate.ON_SITE]
        self.assertFalse(on_site_rule.condition(mock_ctx))

        # Should not trigger when COMPOSTING not enabled
        mock_ctx.production_unit.digestate_valorization_methods = [BiomethaneProductionUnit.SPREADING]
        self.assertFalse(on_site_rule.condition(mock_ctx))

    def test_sale_not_selected_rule_fields_and_condition(self):
        """Test sale rule has correct fields and condition logic."""
        from unittest.mock import Mock

        sale_rule = next(r for r in self.rules if r.name == "sale_not_selected")
        self.assertEqual(sale_rule.fields, BiomethaneDigestateService.SALE_FIELDS)

        # Should trigger when SALE not in spreading management methods
        mock_ctx = Mock()
        mock_ctx.production_unit = Mock()
        mock_ctx.production_unit.spreading_management_methods = ["OTHER_METHOD"]
        self.assertTrue(sale_rule.condition(mock_ctx))

        # Should not trigger when SALE is in spreading management methods
        mock_ctx.production_unit.spreading_management_methods = [BiomethaneProductionUnit.SALE]
        self.assertFalse(sale_rule.condition(mock_ctx))

    def test_wwtp_category_not_2_rule_fields_and_condition(self):
        """Test WWTP category rule has correct fields and condition logic."""
        from unittest.mock import Mock

        wwtp_rule = next(r for r in self.rules if r.name == "wwtp_category_not_2")
        self.assertEqual(wwtp_rule.fields, BiomethaneDigestateService.WWTP_FIELDS)

        # Should trigger when contract category is not 2
        mock_ctx = Mock()
        mock_ctx.contract = Mock()
        mock_ctx.contract.installation_category = BiomethaneContract.INSTALLATION_CATEGORY_1
        self.assertTrue(wwtp_rule.condition(mock_ctx))

        # Should not trigger when contract category is 2
        mock_ctx.contract.installation_category = BiomethaneContract.INSTALLATION_CATEGORY_2
        self.assertFalse(wwtp_rule.condition(mock_ctx))

        # Should not trigger when no contract (rule checks contract existence first)
        mock_ctx.contract = None
        self.assertFalse(wwtp_rule.condition(mock_ctx))


class BiomethaneDigestateServiceIntegrationTests(TestCase):
    """Integration tests verifying end-to-end behavior of the service."""

    def setUp(self):
        self.producer_entity = Entity.objects.create(
            name="Test Producer",
            entity_type=Entity.BIOMETHANE_PRODUCER,
        )
        self.production_unit = BiomethaneProductionUnitFactory.create(producer=self.producer_entity)
        self.contract = BiomethaneContractFactory.create(producer=self.producer_entity)

    def test_get_fields_to_clear_with_phase_separation(self):
        """Test that raw digestate fields are cleared when phase separation is used."""
        digestate = BiomethaneDigestateFactory.create(producer=self.producer_entity)

        # Configure production unit with phase separation
        self.production_unit.has_digestate_phase_separation = True
        self.production_unit.save()

        fields_to_clear = BiomethaneDigestateService.get_fields_to_clear(digestate)

        self.assertIsInstance(fields_to_clear, list)
        self.assertIn("raw_digestate_tonnage_produced", fields_to_clear)
        self.assertIn("raw_digestate_dry_matter_rate", fields_to_clear)

    def test_get_fields_to_clear_without_phase_separation(self):
        """Test that separated digestate fields are cleared when no phase separation."""
        digestate = BiomethaneDigestateFactory.create(producer=self.producer_entity)

        # Configure production unit without phase separation
        self.production_unit.has_digestate_phase_separation = False
        self.production_unit.save()

        fields_to_clear = BiomethaneDigestateService.get_fields_to_clear(digestate)

        self.assertIn("solid_digestate_tonnage", fields_to_clear)
        self.assertIn("liquid_digestate_quantity", fields_to_clear)

    def test_get_fields_to_clear_when_composting_disabled(self):
        """Test that composting fields are cleared when composting is not in valorization methods."""
        digestate = BiomethaneDigestateFactory.create(producer=self.producer_entity)

        # Configure production unit without composting
        self.production_unit.digestate_valorization_methods = [BiomethaneProductionUnit.SPREADING]
        self.production_unit.save()

        fields_to_clear = BiomethaneDigestateService.get_fields_to_clear(digestate)

        self.assertIn("composting_locations", fields_to_clear)
        self.assertIn("external_platform_name", fields_to_clear)
        self.assertIn("on_site_composted_digestate_volume", fields_to_clear)

    def test_get_fields_to_clear_when_external_platform_not_selected(self):
        """Test that external platform fields are cleared when only on-site is selected."""
        digestate = BiomethaneDigestateFactory.create(
            producer=self.producer_entity,
            composting_locations=[BiomethaneDigestate.ON_SITE],
        )

        # Configure production unit with composting
        self.production_unit.digestate_valorization_methods = [BiomethaneProductionUnit.COMPOSTING]
        self.production_unit.save()

        fields_to_clear = BiomethaneDigestateService.get_fields_to_clear(digestate)

        self.assertIn("external_platform_name", fields_to_clear)
        self.assertIn("external_platform_digestate_volume", fields_to_clear)
        # But on-site field should NOT be in the list
        self.assertNotIn("on_site_composted_digestate_volume", fields_to_clear)

    def test_get_fields_to_clear_wwtp_with_category_not_2(self):
        """Test that WWTP fields are cleared when contract category is not 2."""
        digestate = BiomethaneDigestateFactory.create(producer=self.producer_entity)

        # Configure contract with category 1
        self.contract.installation_category = BiomethaneContract.INSTALLATION_CATEGORY_1
        self.contract.save()

        fields_to_clear = BiomethaneDigestateService.get_fields_to_clear(digestate)

        self.assertIn("wwtp_materials_to_incineration", fields_to_clear)

    def test_get_fields_to_clear_deduplicates_fields(self):
        """Test that duplicate fields are removed from the result."""
        digestate = BiomethaneDigestateFactory.create(producer=self.producer_entity)

        # Configure to trigger multiple rules that might return same fields
        self.production_unit.digestate_valorization_methods = []
        self.production_unit.save()

        fields_to_clear = BiomethaneDigestateService.get_fields_to_clear(digestate)

        # Verify no duplicates
        self.assertEqual(len(fields_to_clear), len(set(fields_to_clear)))

    def test_get_optional_fields_returns_same_as_fields_to_clear(self):
        """Test that get_optional_fields returns the same list as get_fields_to_clear."""
        digestate = BiomethaneDigestateFactory.create(producer=self.producer_entity)

        optional_fields = BiomethaneDigestateService.get_optional_fields(digestate)
        fields_to_clear = BiomethaneDigestateService.get_fields_to_clear(digestate)

        self.assertEqual(optional_fields, fields_to_clear)
