from unittest.mock import Mock

from django.test import TestCase

from biomethane.factories import BiomethaneEnergyFactory, BiomethaneProductionUnitFactory
from biomethane.factories.contract import BiomethaneContractFactory
from biomethane.models.biomethane_energy import BiomethaneEnergy
from biomethane.services.energy import BiomethaneEnergyService, EnergyContext, _build_energy_rules
from core.models import Entity


class EnergyContextExtractionTests(TestCase):
    """Unit tests for _extract_data context extraction."""

    def setUp(self):
        self.producer_entity = Entity.objects.create(
            name="Test Producer",
            entity_type=Entity.BIOMETHANE_PRODUCER,
        )

    def test_extract_data_with_production_unit_and_contract(self):
        """Test context extraction when both production unit and contract exist."""
        production_unit = BiomethaneProductionUnitFactory.create(producer=self.producer_entity)
        contract = BiomethaneContractFactory.create(producer=self.producer_entity)
        energy = BiomethaneEnergyFactory.create(producer=self.producer_entity)

        context = BiomethaneEnergyService._extract_data(energy)

        self.assertIsInstance(context, EnergyContext)
        self.assertEqual(context.instance, energy)
        self.assertEqual(context.production_unit, production_unit)
        self.assertEqual(context.contract, contract)

    def test_extract_data_without_production_unit(self):
        """Test context extraction when production unit does not exist."""
        BiomethaneContractFactory.create(producer=self.producer_entity)
        energy = BiomethaneEnergyFactory.create(producer=self.producer_entity)

        context = BiomethaneEnergyService._extract_data(energy)

        self.assertIsInstance(context, EnergyContext)
        self.assertEqual(context.instance, energy)
        self.assertIsNone(context.production_unit)
        self.assertIsNotNone(context.contract)

    def test_extract_data_without_contract(self):
        """Test context extraction when contract does not exist."""
        BiomethaneProductionUnitFactory.create(producer=self.producer_entity)
        energy = BiomethaneEnergyFactory.create(producer=self.producer_entity)

        context = BiomethaneEnergyService._extract_data(energy)

        self.assertIsInstance(context, EnergyContext)
        self.assertEqual(context.instance, energy)
        self.assertIsNotNone(context.production_unit)
        self.assertIsNone(context.contract)

    def test_extract_data_without_producer(self):
        """Test context extraction when energy has no producer."""
        energy = BiomethaneEnergyFactory.build(producer=None)

        context = BiomethaneEnergyService._extract_data(energy)

        self.assertIsInstance(context, EnergyContext)
        self.assertEqual(context.instance, energy)
        self.assertIsNone(context.production_unit)
        self.assertIsNone(context.contract)

    def test_context_properties_access_instance_attributes(self):
        """Test that context properties correctly access instance attributes."""
        energy = BiomethaneEnergyFactory.create(
            producer=self.producer_entity,
            has_malfunctions=True,
            malfunction_types=["TECHNICAL"],
            has_injection_difficulties_due_to_network_saturation=True,
            energy_types=[BiomethaneEnergy.ENERGY_TYPE_FOSSIL],
        )

        context = BiomethaneEnergyService._extract_data(energy)

        self.assertTrue(context.has_malfunctions)
        self.assertEqual(context.malfunction_types, ["TECHNICAL"])
        self.assertTrue(context.has_injection_difficulties)
        self.assertEqual(context.energy_types, [BiomethaneEnergy.ENERGY_TYPE_FOSSIL])

    def test_context_tariff_reference_with_contract(self):
        """Test that tariff_reference property accesses contract correctly."""
        BiomethaneContractFactory.create(
            producer=self.producer_entity,
            tariff_reference="2023",
        )
        energy = BiomethaneEnergyFactory.create(producer=self.producer_entity)

        context = BiomethaneEnergyService._extract_data(energy)

        self.assertEqual(context.tariff_reference, "2023")

    def test_context_tariff_reference_without_contract(self):
        """Test that tariff_reference returns None when no contract."""
        BiomethaneProductionUnitFactory.create(producer=self.producer_entity)
        energy = BiomethaneEnergyFactory.create(producer=self.producer_entity)

        context = BiomethaneEnergyService._extract_data(energy)

        self.assertIsNone(context.tariff_reference)


class EnergyRulesConfigurationTests(TestCase):
    """Unit tests for _build_energy_rules configuration."""

    def setUp(self):
        self.rules = _build_energy_rules()

    def test_all_expected_rules_are_configured(self):
        """Test that all expected rules are present in the configuration."""
        expected_rule_names = [
            "not_old_tariff",
            "not_new_tariff",
            "no_malfunctions",
            "malfunction_no_other_type",
            "no_injection_difficulties",
            "no_fossil_for_energy",
            "no_biogas_or_biomethane_energy_type",
        ]

        actual_rule_names = [rule.name for rule in self.rules]
        self.assertEqual(expected_rule_names, actual_rule_names)

    def test_old_tariff_rule_fields_and_condition(self):
        """Test old tariff rule has correct fields and condition logic."""
        old_tariff_rule = next(r for r in self.rules if r.name == "not_old_tariff")
        self.assertEqual(old_tariff_rule.fields, BiomethaneEnergyService.OLD_TARIFF_FIELDS)

        # Test condition: should trigger when tariff NOT in ["2011", "2020", "2021"]
        mock_ctx = Mock()
        mock_ctx.tariff_reference = "2023"
        self.assertTrue(old_tariff_rule.condition(mock_ctx))

        # Should not trigger when tariff is in the list
        mock_ctx.tariff_reference = "2011"
        self.assertFalse(old_tariff_rule.condition(mock_ctx))

    def test_new_tariff_rule_fields_and_condition(self):
        """Test new tariff rule has correct fields and condition logic."""
        new_tariff_rule = next(r for r in self.rules if r.name == "not_new_tariff")
        self.assertEqual(new_tariff_rule.fields, BiomethaneEnergyService.NEW_TARIFF_FIELDS)

        # Test condition: should trigger when tariff is NOT "2023"
        mock_ctx = Mock()
        mock_ctx.tariff_reference = "2011"
        self.assertTrue(new_tariff_rule.condition(mock_ctx))

        # Should not trigger when tariff is "2023"
        mock_ctx.tariff_reference = "2023"
        self.assertFalse(new_tariff_rule.condition(mock_ctx))

    def test_malfunction_rule_fields_and_condition(self):
        """Test malfunction rules have correct fields and condition logic."""
        no_malfunctions_rule = next(r for r in self.rules if r.name == "no_malfunctions")
        self.assertEqual(no_malfunctions_rule.fields, BiomethaneEnergyService.MALFUNCTION_FIELDS)

        # Test condition: should trigger when has_malfunctions is False
        mock_ctx = Mock()
        mock_ctx.has_malfunctions = False
        self.assertTrue(no_malfunctions_rule.condition(mock_ctx))

        # Should not trigger when has_malfunctions is True
        mock_ctx.has_malfunctions = True
        self.assertFalse(no_malfunctions_rule.condition(mock_ctx))

    def test_malfunction_details_rule_condition(self):
        """Test malfunction_details rule condition logic."""
        malfunction_details_rule = next(r for r in self.rules if r.name == "malfunction_no_other_type")

        # Should trigger when has_malfunctions=True but "OTHER" not in types
        mock_ctx = Mock()
        mock_ctx.has_malfunctions = True
        mock_ctx.malfunction_types = ["MAINTENANCE", "TECHNICAL"]
        self.assertTrue(malfunction_details_rule.condition(mock_ctx))

        # Should not trigger when "OTHER" is in types
        mock_ctx.malfunction_types = ["OTHER"]
        self.assertFalse(malfunction_details_rule.condition(mock_ctx))

        # Should not trigger when has_malfunctions=False
        mock_ctx.has_malfunctions = False
        self.assertFalse(malfunction_details_rule.condition(mock_ctx))

    def test_injection_difficulties_rule_condition(self):
        """Test injection difficulties rule condition logic."""
        injection_rule = next(r for r in self.rules if r.name == "no_injection_difficulties")

        # Should trigger when has_injection_difficulties is False
        mock_ctx = Mock()
        mock_ctx.has_injection_difficulties = False
        self.assertTrue(injection_rule.condition(mock_ctx))

        # Should not trigger when has_injection_difficulties is True
        mock_ctx.has_injection_difficulties = True
        self.assertFalse(injection_rule.condition(mock_ctx))

    def test_fossil_attestation_rules_conditions(self):
        """Test fossil energy rules condition logic."""
        from biomethane.models.biomethane_energy import BiomethaneEnergy

        no_fossil_rule = next(r for r in self.rules if r.name == "no_fossil_for_energy")
        self.assertEqual(no_fossil_rule.fields, ["energy_details"])

        # Test: should trigger when no problematic energy types are present
        mock_ctx = Mock()
        mock_ctx.energy_types = [BiomethaneEnergy.ENERGY_TYPE_PRODUCED_BIOGAS]
        self.assertTrue(no_fossil_rule.condition(mock_ctx))

        # Should trigger when energy_types is empty
        mock_ctx.energy_types = []
        self.assertTrue(no_fossil_rule.condition(mock_ctx))

        # Should not trigger when FOSSIL type is present
        mock_ctx.energy_types = [BiomethaneEnergy.ENERGY_TYPE_FOSSIL]
        self.assertFalse(no_fossil_rule.condition(mock_ctx))

        # Should not trigger when OTHER_RENEWABLE type is present
        mock_ctx.energy_types = [BiomethaneEnergy.ENERGY_TYPE_OTHER_RENEWABLE]
        self.assertFalse(no_fossil_rule.condition(mock_ctx))

        # Should not trigger when OTHER type is present
        mock_ctx.energy_types = [BiomethaneEnergy.ENERGY_TYPE_OTHER]
        self.assertFalse(no_fossil_rule.condition(mock_ctx))

        # Should not trigger when multiple types including problematic one
        mock_ctx.energy_types = [
            BiomethaneEnergy.ENERGY_TYPE_PRODUCED_BIOGAS,
            BiomethaneEnergy.ENERGY_TYPE_FOSSIL,
        ]
        self.assertFalse(no_fossil_rule.condition(mock_ctx))


class BiomethaneEnergyServiceIntegrationTests(TestCase):
    """Integration tests for BiomethaneEnergyService with real Django models."""

    def setUp(self):
        self.producer_entity = Entity.objects.create(
            name="Test Producer",
            entity_type=Entity.BIOMETHANE_PRODUCER,
        )
        self.production_unit = BiomethaneProductionUnitFactory.create(producer=self.producer_entity)
        self.contract = BiomethaneContractFactory.create(producer=self.producer_entity)

    def test_full_integration_malfunction_rules(self):
        """Smoke test: verify malfunction rules work end-to-end."""
        # Case 1: No malfunctions - all fields cleared
        energy = BiomethaneEnergyFactory.create(
            producer=self.producer_entity,
            has_malfunctions=False,
        )
        fields = BiomethaneEnergyService.get_fields_to_clear(energy)
        self.assertIn("malfunction_cumulative_duration_days", fields)
        self.assertIn("malfunction_details", fields)

        # Case 2: Malfunctions but not OTHER - only details cleared
        energy.has_malfunctions = True
        energy.malfunction_types = ["TECHNICAL"]
        energy.save()
        fields = BiomethaneEnergyService.get_fields_to_clear(energy)
        self.assertIn("malfunction_details", fields)
        self.assertNotIn("malfunction_cumulative_duration_days", fields)

        # Case 3: Malfunctions with OTHER - details not cleared
        energy.malfunction_types = [BiomethaneEnergy.MALFUNCTION_TYPE_OTHER]
        energy.save()
        fields = BiomethaneEnergyService.get_fields_to_clear(energy)
        self.assertNotIn("malfunction_details", fields)

    def test_full_integration_tariff_rules(self):
        """Smoke test: verify tariff rules work end-to-end."""
        energy = BiomethaneEnergyFactory.create(
            producer=self.producer_entity,
            energy_types=[BiomethaneEnergy.ENERGY_TYPE_FOSSIL],
            energy_details="test",
        )

        fields = BiomethaneEnergyService.get_fields_to_clear(energy)

        self.assertNotIn("energy_details", fields)

        energy.energy_types = [BiomethaneEnergy.ENERGY_TYPE_PRODUCED_BIOGAS]
        energy.save()
        fields = BiomethaneEnergyService.get_fields_to_clear(energy)
        self.assertIn("energy_details", fields)

    def test_fields_to_clear_returns_deduplicated_list(self):
        """Test that the returned list has no duplicates."""
        energy = BiomethaneEnergyFactory.create(producer=self.producer_entity)
        fields_to_clear = BiomethaneEnergyService.get_fields_to_clear(energy)

        # Check no duplicates
        self.assertEqual(len(fields_to_clear), len(set(fields_to_clear)))

    def test_get_optional_fields_returns_same_as_fields_to_clear(self):
        """Test that get_optional_fields returns the same list as get_fields_to_clear."""
        energy = BiomethaneEnergyFactory.create(
            producer=self.producer_entity,
        )

        optional_fields = BiomethaneEnergyService.get_optional_fields(energy)
        fields_to_clear = BiomethaneEnergyService.get_fields_to_clear(energy)

        self.assertIsInstance(optional_fields, list)
        self.assertEqual(optional_fields, fields_to_clear)
