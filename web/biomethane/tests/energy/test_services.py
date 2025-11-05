from django.test import TestCase

from biomethane.factories import BiomethaneEnergyFactory, BiomethaneProductionUnitFactory
from biomethane.factories.contract import BiomethaneContractFactory
from biomethane.services.energy import BiomethaneEnergyService
from core.models import Entity


class BiomethaneEnergyServiceTests(TestCase):
    def setUp(self):
        self.producer_entity = Entity.objects.create(
            name="Test Producer",
            entity_type=Entity.BIOMETHANE_PRODUCER,
        )
        self.production_unit = BiomethaneProductionUnitFactory.create(producer=self.producer_entity)
        self.contract = BiomethaneContractFactory.create(producer=self.producer_entity)

    def test_get_fields_to_clear_with_malfunction(self):
        """Test that malfunction detail field is cleared when malfunction type is not OTHER."""
        energy = BiomethaneEnergyFactory.create(
            producer=self.producer_entity,
            has_malfunctions=True,
            malfunction_types=["TECHNICAL"],  # Not OTHER
        )

        fields_to_clear = BiomethaneEnergyService.get_fields_to_clear(energy)

        self.assertIsInstance(fields_to_clear, list)
        # When malfunction type is not OTHER, malfunction_details should be cleared
        self.assertIn("malfunction_details", fields_to_clear)

    def test_get_fields_to_clear_without_malfunction(self):
        """Test that all malfunction fields are cleared when no malfunction."""
        energy = BiomethaneEnergyFactory.create(
            producer=self.producer_entity,
            has_malfunctions=False,
        )

        fields_to_clear = BiomethaneEnergyService.get_fields_to_clear(energy)

        # When malfunction is False, all malfunction fields should be cleared
        self.assertIn("malfunction_cumulative_duration_days", fields_to_clear)
        self.assertIn("malfunction_types", fields_to_clear)
        self.assertIn("malfunction_details", fields_to_clear)

    def test_get_fields_to_clear_without_injection_difficulties(self):
        """Test that injection difficulty fields are cleared when not used."""
        energy = BiomethaneEnergyFactory.create(
            producer=self.producer_entity,
            has_injection_difficulties_due_to_network_saturation=False,
        )

        fields_to_clear = BiomethaneEnergyService.get_fields_to_clear(energy)

        # Injection difficulty fields should be cleared
        self.assertIn("injection_impossibility_hours", fields_to_clear)

    def test_get_fields_to_clear_when_no_specific_conditions(self):
        """Test that conditional fields are cleared when conditions are not met."""
        energy = BiomethaneEnergyFactory.create(
            producer=self.producer_entity,
            has_malfunctions=False,
            has_injection_difficulties_due_to_network_saturation=False,
        )

        fields_to_clear = BiomethaneEnergyService.get_fields_to_clear(energy)

        self.assertIsInstance(fields_to_clear, list)

        # Both malfunction and injection difficulty fields should be cleared
        self.assertIn("malfunction_cumulative_duration_days", fields_to_clear)
        self.assertIn("injection_impossibility_hours", fields_to_clear)

    def test_get_optional_fields_returns_same_as_fields_to_clear(self):
        """Test that get_optional_fields returns the same list as get_fields_to_clear."""
        energy = BiomethaneEnergyFactory.create(
            producer=self.producer_entity,
        )

        optional_fields = BiomethaneEnergyService.get_optional_fields(energy)
        fields_to_clear = BiomethaneEnergyService.get_fields_to_clear(energy)

        self.assertIsInstance(optional_fields, list)
        self.assertEqual(optional_fields, fields_to_clear)
