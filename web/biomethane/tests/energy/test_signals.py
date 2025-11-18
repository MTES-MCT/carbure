from unittest.mock import Mock, patch

from django.test import TestCase

from biomethane.factories import BiomethaneEnergyFactory, BiomethaneProductionUnitFactory
from biomethane.factories.contract import BiomethaneContractFactory
from biomethane.models import BiomethaneContract, BiomethaneProductionUnit
from biomethane.models.biomethane_energy import BiomethaneEnergy, clear_energy_fields_on_related_model_save
from core.models import Entity


class ClearEnergyFieldsSignalTests(TestCase):
    """
    Unit tests for clear_energy_fields_on_related_model_save signal handler.

    These tests verify the signal handler's logic without testing Django's signal mechanism itself.
    Business logic is tested in test_services.py.
    """

    def setUp(self):
        self.producer_entity = Entity.objects.create(
            name="Test Producer",
            entity_type=Entity.BIOMETHANE_PRODUCER,
        )

    @patch("biomethane.services.energy.BiomethaneEnergyService.get_fields_to_clear")
    @patch("biomethane.models.biomethane_energy.BiomethaneEnergy.objects.filter")
    def test_handler_with_energy_sender_calls_service_and_updates(self, mock_filter, mock_get_fields):
        """Test handler correctly processes BiomethaneEnergy as sender."""
        # Setup
        energy = BiomethaneEnergyFactory.create(producer=self.producer_entity)

        # Configure mocks after creation
        mock_get_fields.reset_mock()
        mock_filter.reset_mock()
        mock_get_fields.return_value = ["field1", "field2"]
        mock_queryset = Mock()
        mock_filter.return_value = mock_queryset

        # Execute
        clear_energy_fields_on_related_model_save(
            sender=BiomethaneEnergy,
            instance=energy,
        )

        # Verify service was called with energy instance
        mock_get_fields.assert_called_once_with(energy)

        # Verify update was called with correct data
        mock_filter.assert_called_once_with(pk=energy.pk)
        mock_queryset.update.assert_called_once_with(field1=None, field2=None)

    @patch("biomethane.services.energy.BiomethaneEnergyService.get_fields_to_clear")
    @patch("biomethane.models.biomethane_energy.BiomethaneEnergy.objects.filter")
    def test_handler_with_production_unit_sender_gets_latest_energy(self, mock_filter, mock_get_fields):
        """Test handler retrieves latest energy when sender is BiomethaneProductionUnit."""
        # Setup - create multiple energies with different years
        production_unit = BiomethaneProductionUnitFactory.create(producer=self.producer_entity)
        BiomethaneEnergyFactory.create(producer=self.producer_entity, year=2022)
        BiomethaneEnergyFactory.create(producer=self.producer_entity, year=2023)
        energy_2024 = BiomethaneEnergyFactory.create(producer=self.producer_entity, year=2024)

        # Configure mocks after creation
        mock_get_fields.reset_mock()
        mock_get_fields.return_value = ["field1"]

        # Execute
        clear_energy_fields_on_related_model_save(
            sender=BiomethaneProductionUnit,
            instance=production_unit,
        )

        # Verify service was called with the latest energy (year 2024)
        mock_get_fields.assert_called_once_with(energy_2024)

    @patch("biomethane.services.energy.BiomethaneEnergyService.get_fields_to_clear")
    @patch("biomethane.models.biomethane_energy.BiomethaneEnergy.objects.filter")
    def test_handler_with_contract_sender_gets_latest_energy(self, mock_filter, mock_get_fields):
        """Test handler retrieves latest energy when sender is BiomethaneContract."""
        # Setup - create multiple energies with different years
        buyer = Entity.objects.create(name="Buyer", entity_type=Entity.OPERATOR)
        contract = BiomethaneContractFactory.create(producer=self.producer_entity, buyer=buyer)
        BiomethaneEnergyFactory.create(producer=self.producer_entity, year=2022)
        BiomethaneEnergyFactory.create(producer=self.producer_entity, year=2023)
        energy_2024 = BiomethaneEnergyFactory.create(producer=self.producer_entity, year=2024)

        # Configure mocks after creation
        mock_get_fields.reset_mock()
        mock_get_fields.return_value = ["field1"]

        # Execute
        clear_energy_fields_on_related_model_save(
            sender=BiomethaneContract,
            instance=contract,
        )

        # Verify service was called with the latest energy (year 2024)
        mock_get_fields.assert_called_once_with(energy_2024)

    @patch("biomethane.services.energy.BiomethaneEnergyService.get_fields_to_clear")
    @patch("biomethane.models.biomethane_energy.BiomethaneEnergy.objects.filter")
    def test_handler_does_nothing_when_no_energy_exists(self, mock_filter, mock_get_fields):
        """Test handler exits gracefully when no energy instance exists."""
        # Setup - production unit without any energy
        production_unit = BiomethaneProductionUnitFactory.create(producer=self.producer_entity)
        # No energy created

        # Execute
        clear_energy_fields_on_related_model_save(
            sender=BiomethaneProductionUnit,
            instance=production_unit,
        )

        # Verify nothing was called
        mock_get_fields.assert_not_called()
        mock_filter.assert_not_called()

    @patch("biomethane.services.energy.BiomethaneEnergyService.get_fields_to_clear")
    @patch("biomethane.models.biomethane_energy.BiomethaneEnergy.objects.filter")
    def test_handler_does_not_update_when_no_fields_to_clear(self, mock_filter, mock_get_fields):
        """Test handler does not call update when service returns empty list."""
        # Setup
        energy = BiomethaneEnergyFactory.create(producer=self.producer_entity)

        # Configure mocks after creation
        mock_get_fields.reset_mock()
        mock_filter.reset_mock()
        mock_get_fields.return_value = []  # No fields to clear

        # Execute
        clear_energy_fields_on_related_model_save(
            sender=BiomethaneEnergy,
            instance=energy,
        )

        # Verify nothing was called
        mock_get_fields.assert_called_once_with(energy)
        mock_filter.assert_not_called()

    @patch("biomethane.services.energy.BiomethaneEnergyService.get_fields_to_clear")
    @patch("biomethane.models.biomethane_energy.BiomethaneEnergy.objects.filter")
    def test_handler_ignores_unknown_sender(self, mock_filter, mock_get_fields):
        """Test handler exits early when sender is not a recognized model."""
        # Setup
        entity = Entity.objects.create(name="Random Entity", entity_type=Entity.OPERATOR)

        # Execute with unknown sender
        clear_energy_fields_on_related_model_save(
            sender=Entity,  # Not BiomethaneEnergy, BiomethaneProductionUnit, or BiomethaneContract
            instance=entity,
        )

        # Verify nothing was called
        mock_get_fields.assert_not_called()
        mock_filter.assert_not_called()
