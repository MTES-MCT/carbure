from unittest.mock import patch

from django.test import TestCase

from biomethane.factories.contract import BiomethaneContractFactory
from biomethane.models import BiomethaneContract
from core.models import Entity


class RedIISignalTests(TestCase):
    """
    Unit tests for the update_red_ii_status signal.

    This signal has specific business logic (RED II status calculation)
    that needs to be tested directly, not mocked.
    """

    def setUp(self):
        """Initial setup for signal tests."""
        self.producer_entity = Entity.objects.create(
            name="Test Producer",
            entity_type=Entity.BIOMETHANE_PRODUCER,
        )

        self.buyer_entity = Entity.objects.create(
            name="Test Buyer",
            entity_type=Entity.OPERATOR,
        )

    def test_signal_sets_red_ii_true_when_cmax_above_threshold(self):
        """Signal should set is_red_ii=True when cmax > 200."""
        self.assertFalse(self.producer_entity.is_red_ii)

        BiomethaneContractFactory.create(
            producer=self.producer_entity,
            buyer=self.buyer_entity,
            tariff_reference="2011",
            cmax=250.0,  # > 200
        )

        self.producer_entity.refresh_from_db()
        self.assertTrue(self.producer_entity.is_red_ii)

    def test_signal_sets_red_ii_true_when_pap_above_threshold(self):
        """Signal should set is_red_ii=True when pap_contracted > 19.5."""
        self.assertFalse(self.producer_entity.is_red_ii)

        BiomethaneContractFactory.create(
            producer=self.producer_entity,
            buyer=self.buyer_entity,
            tariff_reference="2021",
            pap_contracted=25.0,  # > 19.5
        )

        self.producer_entity.refresh_from_db()
        self.assertTrue(self.producer_entity.is_red_ii)

    def test_signal_no_change_when_below_thresholds(self):
        """Signal should not change is_red_ii when values are below thresholds."""
        self.assertFalse(self.producer_entity.is_red_ii)

        BiomethaneContractFactory.create(
            producer=self.producer_entity,
            buyer=self.buyer_entity,
            tariff_reference="2011",
            cmax=150.0,  # <= 200
        )

        self.producer_entity.refresh_from_db()
        self.assertFalse(self.producer_entity.is_red_ii)

    def test_signal_on_contract_update(self):
        """Signal should trigger on contract updates."""
        # Create initial contract below threshold
        contract = BiomethaneContractFactory.create(
            producer=self.producer_entity,
            buyer=self.buyer_entity,
            tariff_reference="2011",
            cmax=100.0,  # <= 200
        )

        self.producer_entity.refresh_from_db()
        self.assertFalse(self.producer_entity.is_red_ii)

        # Update contract to trigger signal
        contract.cmax = 300.0  # > 200
        contract.save()

        self.producer_entity.refresh_from_db()
        self.assertTrue(self.producer_entity.is_red_ii)

    def test_signal_does_not_override_existing_red_ii_true(self):
        """Signal should not change is_red_ii when already True."""
        # Set producer as RED II
        self.producer_entity.is_red_ii = True
        self.producer_entity.save()

        # Create contract with values below thresholds
        BiomethaneContractFactory.create(
            producer=self.producer_entity,
            buyer=self.buyer_entity,
            tariff_reference="2011",
            cmax=100.0,  # <= 200
        )

        self.producer_entity.refresh_from_db()
        # Should remain True (signal returns early if already True)
        self.assertTrue(self.producer_entity.is_red_ii)


class ClearFieldsSignalTests(TestCase):
    """
    Unit tests for the clear_contract_fields_on_save signal handler.

    These tests verify that the handler function correctly:
    - Calls the service layer to determine fields to clear
    - Updates the database when service returns field updates
    - Skips database updates when service returns empty dict
    """

    @patch("biomethane.services.contract.BiomethaneContractService.clear_fields_based_on_tariff")
    @patch("biomethane.models.biomethane_contract.BiomethaneContract.objects.filter")
    def test_handler_calls_service_with_instance(self, mock_filter, mock_clear_fields):
        """Test that handler calls service with contract instance"""
        from biomethane.factories import BiomethaneContractFactory
        from biomethane.models.biomethane_contract import clear_contract_fields_on_save

        mock_clear_fields.return_value = {}
        contract = BiomethaneContractFactory.create()

        clear_contract_fields_on_save(sender=BiomethaneContract, instance=contract)

        mock_clear_fields.assert_called_with(contract)

    @patch("biomethane.services.contract.BiomethaneContractService.clear_fields_based_on_tariff")
    @patch("biomethane.models.biomethane_contract.BiomethaneContract.objects.filter")
    def test_handler_updates_database_when_service_returns_fields(self, mock_filter, mock_clear_fields):
        """Test that handler updates database when service returns field updates"""
        from biomethane.factories import BiomethaneContractFactory
        from biomethane.models.biomethane_contract import clear_contract_fields_on_save

        mock_clear_fields.return_value = {"pap_contracted": None, "cmax_annualized_value": None}
        contract = BiomethaneContractFactory.create()

        mock_queryset = mock_filter.return_value
        clear_contract_fields_on_save(sender=BiomethaneContract, instance=contract)

        mock_filter.assert_called_with(pk=contract.pk)
        mock_queryset.update.assert_called_with(pap_contracted=None, cmax_annualized_value=None)

    @patch("biomethane.services.contract.BiomethaneContractService.clear_fields_based_on_tariff")
    @patch("biomethane.models.biomethane_contract.BiomethaneContract.objects.filter")
    def test_handler_skips_update_when_service_returns_empty_dict(self, mock_filter, mock_clear_fields):
        """Test that handler skips database update when service returns empty dict"""
        from biomethane.factories import BiomethaneContractFactory
        from biomethane.models.biomethane_contract import clear_contract_fields_on_save

        mock_clear_fields.return_value = {}
        contract = BiomethaneContractFactory.create()

        clear_contract_fields_on_save(sender=BiomethaneContract, instance=contract)

        # Filter should not be called when update_data is empty
        mock_filter.assert_not_called()
