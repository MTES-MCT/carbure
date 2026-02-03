from unittest.mock import Mock, patch

from django.test import TestCase

from biomethane.factories import BiomethaneEnergyFactory, BiomethaneProductionUnitFactory
from biomethane.factories.contract import BiomethaneContractFactory
from biomethane.models import BiomethaneContract, BiomethaneProductionUnit
from biomethane.models.biomethane_energy import (
    BiomethaneEnergy,
    clear_energy_fields_on_related_model_save,
)
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
        production_unit = BiomethaneProductionUnitFactory.create(created_by=self.producer_entity)
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
        production_unit = BiomethaneProductionUnitFactory.create(created_by=self.producer_entity)
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


class UpdateEnergyFieldsOnContractSaveTests(TestCase):
    """
    Unit tests for update_energy_fields_on_contract_save signal handler.

    These tests verify that the handler correctly clears energy_types field
    when tariff_reference or installation_category changes on a BiomethaneContract.
    """

    def setUp(self):
        self.producer_entity = Entity.objects.create(
            name="Test Producer",
            entity_type=Entity.BIOMETHANE_PRODUCER,
        )
        self.buyer_entity = Entity.objects.create(
            name="Test Buyer",
            entity_type=Entity.OPERATOR,
        )

    def test_clears_energy_types_when_tariff_reference_changes(self):
        """Test that energy_types is cleared when tariff_reference changes."""
        # Setup - create contract and energy with energy_types
        contract = BiomethaneContractFactory.create(
            producer=self.producer_entity,
            buyer=self.buyer_entity,
            tariff_reference="2011",
        )
        energy = BiomethaneEnergyFactory.create(
            producer=self.producer_entity,
            year=2024,
            energy_types=["PRODUCED_BIOGAS", "FOSSIL"],
        )

        # Verify initial state
        energy.refresh_from_db()
        self.assertEqual(energy.energy_types, ["PRODUCED_BIOGAS", "FOSSIL"])

        # Update tariff_reference
        contract.tariff_reference = "2021"
        contract.save()

        # Verify energy_types was cleared
        energy.refresh_from_db()
        self.assertIsNone(energy.energy_types)

    def test_clears_energy_types_when_installation_category_changes(self):
        """Test that energy_types is cleared when installation_category changes."""
        # Setup - create contract and energy with energy_types
        contract = BiomethaneContractFactory.create(
            producer=self.producer_entity,
            buyer=self.buyer_entity,
            tariff_reference="2011",
            installation_category=BiomethaneContract.INSTALLATION_CATEGORY_1,
        )
        energy = BiomethaneEnergyFactory.create(
            producer=self.producer_entity,
            year=2024,
            energy_types=["PRODUCED_BIOGAS"],
        )

        # Verify initial state
        energy.refresh_from_db()
        self.assertEqual(energy.energy_types, ["PRODUCED_BIOGAS"])

        # Update installation_category
        contract.installation_category = BiomethaneContract.INSTALLATION_CATEGORY_2
        contract.save()

        # Verify energy_types was cleared
        energy.refresh_from_db()
        self.assertIsNone(energy.energy_types)

    def test_does_not_clear_energy_types_when_fields_unchanged(self):
        """Test that energy_types is not cleared when fields don't change."""
        # Setup - create contract and energy with energy_types
        contract = BiomethaneContractFactory.create(
            producer=self.producer_entity,
            buyer=self.buyer_entity,
            tariff_reference="2011",
            installation_category=BiomethaneContract.INSTALLATION_CATEGORY_1,
        )
        energy = BiomethaneEnergyFactory.create(
            producer=self.producer_entity,
            year=2024,
            energy_types=["PRODUCED_BIOGAS"],
        )

        # Update a different field (not tariff_reference or installation_category)
        contract.cmax = 150.0
        contract.save()

        # Verify energy_types was NOT cleared
        energy.refresh_from_db()
        self.assertEqual(energy.energy_types, ["PRODUCED_BIOGAS"])

    def test_updates_latest_energy_when_multiple_energies_exist(self):
        """Test that only the latest energy (highest year) is updated."""
        # Setup - create multiple energies with different years
        contract = BiomethaneContractFactory.create(
            producer=self.producer_entity,
            buyer=self.buyer_entity,
            tariff_reference="2011",
        )
        energy_2022 = BiomethaneEnergyFactory.create(
            producer=self.producer_entity,
            year=2022,
            energy_types=["PRODUCED_BIOGAS"],
        )
        energy_2023 = BiomethaneEnergyFactory.create(
            producer=self.producer_entity,
            year=2023,
            energy_types=["FOSSIL"],
        )
        energy_2024 = BiomethaneEnergyFactory.create(
            producer=self.producer_entity,
            year=2024,
            energy_types=["PRODUCED_BIOMETHANE"],
        )

        # Update tariff_reference
        contract.tariff_reference = "2021"
        contract.save()

        # Verify only the latest energy (2024) was cleared
        energy_2022.refresh_from_db()
        energy_2023.refresh_from_db()
        energy_2024.refresh_from_db()
        self.assertEqual(energy_2022.energy_types, ["PRODUCED_BIOGAS"])
        self.assertEqual(energy_2023.energy_types, ["FOSSIL"])
        self.assertIsNone(energy_2024.energy_types)

    def test_handles_no_energy_instance_gracefully(self):
        """Test that handler doesn't fail when no energy instance exists."""
        # Setup - create contract without any energy
        contract = BiomethaneContractFactory.create(
            producer=self.producer_entity,
            buyer=self.buyer_entity,
            tariff_reference="2011",
        )
        # No energy created

        # Update tariff_reference - should not raise an error
        contract.tariff_reference = "2021"
        contract.save()  # Should complete without error

    def test_handles_contract_creation_gracefully(self):
        """Test that handler handles new contract creation without failing and doesn't clear energy_types."""
        # Setup - create energy first
        energy = BiomethaneEnergyFactory.create(
            producer=self.producer_entity,
            year=2024,
            energy_types=["PRODUCED_BIOGAS"],
        )

        # Create a new contract - should handle the case where contract doesn't have pk yet
        # During creation, old_contract will be None, so energy_types shouldn't be cleared
        BiomethaneContractFactory.create(
            producer=self.producer_entity,
            buyer=self.buyer_entity,
            tariff_reference="2011",
        )

        # Verify energy_types is still set (creation shouldn't clear it)
        energy.refresh_from_db()
        self.assertEqual(energy.energy_types, ["PRODUCED_BIOGAS"])
