from django.test import TestCase

from biomethane.factories.production_unit import BiomethaneProductionUnitFactory
from biomethane.models import BiomethaneProductionUnit
from core.models import Entity
from core.tests_utils import assert_object_contains_data


class BiomethaneProductionUnitSignalTests(TestCase):
    """Unit tests for BiomethaneProductionUnit signals."""

    def setUp(self):
        """Initial setup for signal tests."""
        self.producer_entity = Entity.objects.create(
            name="Test Producer",
            entity_type=Entity.BIOMETHANE_PRODUCER,
        )

    def test_clear_all_fields_when_conditions_trigger_all_branches_with_phase_separation(self):
        """
        Test that all fields are cleared when all conditions trigger all branches.
        This test covers: has_sanitary_approval=False, has_hygienization_exemption=False,
        has_digestate_phase_separation=True, and SPREADING not in digestate_valorization_methods.
        """
        initial_fields = {
            "has_sanitary_approval": False,
            "sanitary_approval_number": "APPROVAL123",
            "has_hygienization_exemption": False,
            "hygienization_exemption_type": BiomethaneProductionUnit.TOTAL,
            "has_digestate_phase_separation": True,
            "raw_digestate_treatment_steps": "Raw treatment steps",
            "liquid_phase_treatment_steps": "Liquid treatment steps",
            "solid_phase_treatment_steps": "Solid treatment steps",
            "digestate_valorization_methods": [BiomethaneProductionUnit.COMPOSTING],
            "spreading_management_methods": [BiomethaneProductionUnit.DIRECT_SPREADING],
        }
        # Create production unit with all fields that should be cleared
        production_unit = BiomethaneProductionUnitFactory.create(producer=self.producer_entity, **initial_fields)

        # Verify initial state
        assert_object_contains_data(self, production_unit, initial_fields)

        # Save to trigger signal
        production_unit.save()

        # Reload from database and verify all fields are cleared
        production_unit.refresh_from_db()
        expected_fields = {
            "sanitary_approval_number": None,
            "hygienization_exemption_type": None,
            "raw_digestate_treatment_steps": None,
            "liquid_phase_treatment_steps": None,
            "solid_phase_treatment_steps": None,
            "spreading_management_methods": [],
        }
        assert_object_contains_data(self, production_unit, expected_fields)

    def test_clear_all_fields_when_conditions_triggers_without_phase_separation(self):
        """
        Test that all fields are cleared when conditions triggers without phase separation.
        This test covers: has_digestate_phase_separation=False.
        """
        initial_fields = {
            "has_digestate_phase_separation": False,
            "raw_digestate_treatment_steps": "Raw treatment steps",
            "liquid_phase_treatment_steps": "Liquid treatment steps",
            "solid_phase_treatment_steps": "Solid treatment steps",
        }
        # Create production unit with all fields that should be cleared
        production_unit = BiomethaneProductionUnitFactory.create(producer=self.producer_entity, **initial_fields)

        # Verify initial state
        assert_object_contains_data(self, production_unit, initial_fields)

        # Save to trigger signal
        production_unit.save()

        # Reload from database and verify all fields are cleared
        production_unit.refresh_from_db()
        expected_fields = {
            "raw_digestate_treatment_steps": None,
            "liquid_phase_treatment_steps": None,
            "solid_phase_treatment_steps": None,
        }
        assert_object_contains_data(self, production_unit, expected_fields)

    def test_preserve_fields_when_conditions_remain_true(self):
        """Test fields are preserved when boolean conditions remain True."""
        production_unit = BiomethaneProductionUnitFactory.create(
            producer=self.producer_entity,
            has_sanitary_approval=True,
            sanitary_approval_number="APPROVAL_PRESERVED",
            has_hygienization_exemption=True,
            hygienization_exemption_type=BiomethaneProductionUnit.TOTAL,
            has_digestate_phase_separation=False,
            raw_digestate_treatment_steps="Raw treatment preserved",
            digestate_valorization_methods=[BiomethaneProductionUnit.SPREADING],
            spreading_management_methods=[BiomethaneProductionUnit.DIRECT_SPREADING],
        )

        # Verify initial state
        self.assertEqual(production_unit.sanitary_approval_number, "APPROVAL_PRESERVED")
        self.assertEqual(production_unit.hygienization_exemption_type, BiomethaneProductionUnit.TOTAL)
        self.assertEqual(production_unit.raw_digestate_treatment_steps, "Raw treatment preserved")
        self.assertEqual(production_unit.spreading_management_methods, [BiomethaneProductionUnit.DIRECT_SPREADING])

        # Update only unit_name (other fields should remain)
        production_unit.unit_name = "Updated Unit Name"
        production_unit.save()

        # Reload from database and verify dependent fields are preserved
        production_unit.refresh_from_db()
        self.assertEqual(production_unit.unit_name, "Updated Unit Name")
        self.assertEqual(production_unit.sanitary_approval_number, "APPROVAL_PRESERVED")
        self.assertEqual(production_unit.hygienization_exemption_type, BiomethaneProductionUnit.TOTAL)
        self.assertEqual(production_unit.raw_digestate_treatment_steps, "Raw treatment preserved")
        self.assertEqual(production_unit.spreading_management_methods, [BiomethaneProductionUnit.DIRECT_SPREADING])
