from unittest.mock import Mock, patch

from django.test import TestCase

from biomethane.factories.contract import BiomethaneContractFactory
from biomethane.factories.digestate import BiomethaneDigestateFactory
from biomethane.factories.production_unit import BiomethaneProductionUnitFactory
from biomethane.models.biomethane_contract import BiomethaneContract
from biomethane.models.biomethane_digestate import BiomethaneDigestate, clear_digestate_fields_on_related_model_save
from biomethane.models.biomethane_production_unit import BiomethaneProductionUnit
from core.models import Entity


class ClearDigestateFieldsSignalTests(TestCase):
    """
    Unit tests for clear_digestate_fields_on_related_model_save signal handler.

    These tests verify the signal handler's logic without testing Django's signal mechanism itself.
    Business logic is tested in test_services.py.
    """

    def setUp(self):
        self.producer_entity = Entity.objects.create(
            name="Test Producer",
            entity_type=Entity.BIOMETHANE_PRODUCER,
        )

    @patch("biomethane.services.digestate.BiomethaneDigestateService.get_fields_to_clear")
    @patch("biomethane.models.biomethane_digestate.BiomethaneDigestate.objects.filter")
    def test_handler_with_digestate_sender_calls_service_and_updates(self, mock_filter, mock_get_fields):
        """Test handler correctly processes BiomethaneDigestate as sender."""
        # Setup
        digestate = BiomethaneDigestateFactory.create(producer=self.producer_entity)

        # Configure mocks after creation
        mock_get_fields.reset_mock()
        mock_filter.reset_mock()
        mock_get_fields.return_value = ["field1", "field2"]
        mock_queryset = Mock()
        mock_filter.return_value = mock_queryset

        # Execute
        clear_digestate_fields_on_related_model_save(
            sender=BiomethaneDigestate,
            instance=digestate,
        )

        # Verify service was called with digestate instance
        mock_get_fields.assert_called_once_with(digestate)

        # Verify update was called with correct data
        mock_filter.assert_called_once_with(pk=digestate.pk)
        mock_queryset.update.assert_called_once_with(field1=None, field2=None)

    @patch("biomethane.services.digestate.BiomethaneDigestateService.get_fields_to_clear")
    @patch("biomethane.models.biomethane_digestate.BiomethaneDigestate.objects.filter")
    def test_handler_with_production_unit_sender_gets_latest_digestate(self, mock_filter, mock_get_fields):
        """Test handler retrieves latest digestate when sender is BiomethaneProductionUnit."""
        # Setup - create multiple digestates with different years
        production_unit = BiomethaneProductionUnitFactory.create(created_by=self.producer_entity)
        BiomethaneDigestateFactory.create(producer=self.producer_entity, year=2022)
        BiomethaneDigestateFactory.create(producer=self.producer_entity, year=2023)
        digestate_2024 = BiomethaneDigestateFactory.create(producer=self.producer_entity, year=2024)

        # Configure mocks after creation
        mock_get_fields.reset_mock()
        mock_get_fields.return_value = ["field1"]

        # Execute
        clear_digestate_fields_on_related_model_save(
            sender=BiomethaneProductionUnit,
            instance=production_unit,
        )

        # Verify service was called with the latest digestate (year 2024)
        mock_get_fields.assert_called_once_with(digestate_2024)

    @patch("biomethane.services.digestate.BiomethaneDigestateService.get_fields_to_clear")
    @patch("biomethane.models.biomethane_digestate.BiomethaneDigestate.objects.filter")
    def test_handler_with_contract_sender_gets_latest_digestate(self, mock_filter, mock_get_fields):
        """Test handler retrieves latest digestate when sender is BiomethaneContract."""
        # Setup - create multiple digestates with different years
        buyer = Entity.objects.create(name="Buyer", entity_type=Entity.OPERATOR)
        contract = BiomethaneContractFactory.create(producer=self.producer_entity, buyer=buyer)
        BiomethaneDigestateFactory.create(producer=self.producer_entity, year=2022)
        BiomethaneDigestateFactory.create(producer=self.producer_entity, year=2023)
        digestate_2024 = BiomethaneDigestateFactory.create(producer=self.producer_entity, year=2024)

        # Configure mocks after creation
        mock_get_fields.reset_mock()
        mock_get_fields.return_value = ["field1"]

        # Execute
        clear_digestate_fields_on_related_model_save(
            sender=BiomethaneContract,
            instance=contract,
        )

        # Verify service was called with the latest digestate (year 2024)
        mock_get_fields.assert_called_once_with(digestate_2024)

    @patch("biomethane.services.digestate.BiomethaneDigestateService.get_fields_to_clear")
    @patch("biomethane.models.biomethane_digestate.BiomethaneDigestate.objects.filter")
    def test_handler_does_nothing_when_no_digestate_exists(self, mock_filter, mock_get_fields):
        """Test handler exits gracefully when no digestate instance exists."""
        # Setup - production unit without any digestate
        production_unit = BiomethaneProductionUnitFactory.create(created_by=self.producer_entity)
        # No digestate created

        # Execute
        clear_digestate_fields_on_related_model_save(
            sender=BiomethaneProductionUnit,
            instance=production_unit,
        )

        # Verify service was NOT called
        mock_get_fields.assert_not_called()
        mock_filter.assert_not_called()

    @patch("biomethane.services.digestate.BiomethaneDigestateService.get_fields_to_clear")
    @patch("biomethane.models.biomethane_digestate.BiomethaneDigestate.objects.filter")
    def test_handler_does_not_update_when_no_fields_to_clear(self, mock_filter, mock_get_fields):
        """Test handler does not call update when service returns empty list."""
        # Setup
        digestate = BiomethaneDigestateFactory.create(producer=self.producer_entity)

        # Configure mocks after creation
        mock_get_fields.reset_mock()
        mock_filter.reset_mock()
        mock_get_fields.return_value = []  # No fields to clear

        # Execute
        clear_digestate_fields_on_related_model_save(
            sender=BiomethaneDigestate,
            instance=digestate,
        )

        # Verify service was called
        mock_get_fields.assert_called_once_with(digestate)

        # Verify update was NOT called
        mock_filter.assert_not_called()

    @patch("biomethane.services.digestate.BiomethaneDigestateService.get_fields_to_clear")
    @patch("biomethane.models.biomethane_digestate.BiomethaneDigestate.objects.filter")
    def test_handler_sets_composting_locations_to_empty_list(self, mock_filter, mock_get_fields):
        """Test handler sets composting_locations to empty list instead of None."""
        # Setup
        digestate = BiomethaneDigestateFactory.create(producer=self.producer_entity)

        # Configure mocks after creation
        mock_get_fields.reset_mock()
        mock_filter.reset_mock()
        mock_get_fields.return_value = ["composting_locations", "other_field"]
        mock_queryset = Mock()
        mock_filter.return_value = mock_queryset

        # Execute
        clear_digestate_fields_on_related_model_save(
            sender=BiomethaneDigestate,
            instance=digestate,
        )

        # Verify update was called with empty list for composting_locations
        mock_queryset.update.assert_called_once_with(composting_locations=[], other_field=None)

    @patch("biomethane.services.digestate.BiomethaneDigestateService.get_fields_to_clear")
    @patch("biomethane.models.biomethane_digestate.BiomethaneDigestate.objects.filter")
    def test_handler_ignores_unknown_sender(self, mock_filter, mock_get_fields):
        """Test handler exits early when sender is not a recognized model."""
        # Setup
        entity = Entity.objects.create(name="Random Entity", entity_type=Entity.OPERATOR)

        # Execute with unknown sender
        clear_digestate_fields_on_related_model_save(
            sender=Entity,  # Not BiomethaneDigestate, BiomethaneProductionUnit, or BiomethaneContract
            instance=entity,
        )

        # Verify nothing was called
        mock_get_fields.assert_not_called()
        mock_filter.assert_not_called()
