from django.test import TestCase

from biomethane.factories.contract import BiomethaneContractFactory
from biomethane.models import BiomethaneContract
from core.models import Entity


class RedIISignalTests(TestCase):
    """Unit tests for the update_red_ii_status signal."""

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


class ClearFieldsSignalTests(TestCase):
    """Unit tests for the clear_contract_fields_on_save signal."""

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

    def test_signal_clears_pap_contracted_for_tariff_rule_1(self):
        """Signal should clear pap_contracted for tariff reference in RULE_1 (2011-2020)."""
        # Test for 2011
        contract = BiomethaneContract.objects.create(
            producer=self.producer_entity,
            buyer=self.buyer_entity,
            tariff_reference="2011",
            installation_category=BiomethaneContract.INSTALLATION_CATEGORY_1,
            cmax=150.0,
            cmax_annualized=True,
            cmax_annualized_value=100.0,
            pap_contracted=25.0,  # This should be cleared
        )

        contract.refresh_from_db()
        self.assertIsNone(contract.pap_contracted)
        # Other fields should remain
        self.assertEqual(contract.cmax, 150.0)
        self.assertTrue(contract.cmax_annualized)
        self.assertEqual(contract.cmax_annualized_value, 100.0)

    def test_signal_clears_pap_contracted_for_tariff_2020(self):
        """Signal should clear pap_contracted for tariff reference 2020."""
        contract = BiomethaneContract.objects.create(
            producer=self.producer_entity,
            buyer=self.buyer_entity,
            tariff_reference="2020",
            installation_category=BiomethaneContract.INSTALLATION_CATEGORY_1,
            cmax=150.0,
            cmax_annualized=True,
            cmax_annualized_value=100.0,
            pap_contracted=25.0,  # This should be cleared
        )

        contract.refresh_from_db()
        self.assertIsNone(contract.pap_contracted)

    def test_signal_clears_cmax_fields_for_tariff_rule_2(self):
        """Signal should clear cmax, cmax_annualized, cmax_annualized_value for tariff reference in RULE_2 (2021-2023)."""
        # Test for 2021
        contract = BiomethaneContract.objects.create(
            producer=self.producer_entity,
            buyer=self.buyer_entity,
            tariff_reference="2021",
            cmax=150.0,  # This should be cleared
            cmax_annualized=True,  # This should be set to False
            cmax_annualized_value=100.0,  # This should be cleared
            pap_contracted=25.0,
        )

        contract.refresh_from_db()
        self.assertIsNone(contract.cmax)
        self.assertFalse(contract.cmax_annualized)  # Set to False, not None
        self.assertIsNone(contract.cmax_annualized_value)
        # pap_contracted should remain
        self.assertEqual(contract.pap_contracted, 25.0)

    def test_signal_clears_cmax_fields_for_tariff_2023(self):
        """Signal should clear cmax fields for tariff reference 2023."""
        contract = BiomethaneContract.objects.create(
            producer=self.producer_entity,
            buyer=self.buyer_entity,
            tariff_reference="2023",
            cmax=150.0,  # This should be cleared
            cmax_annualized=True,  # This should be set to False
            cmax_annualized_value=100.0,  # This should be cleared
            pap_contracted=25.0,
        )

        contract.refresh_from_db()
        self.assertIsNone(contract.cmax)
        self.assertFalse(contract.cmax_annualized)
        self.assertIsNone(contract.cmax_annualized_value)

    def test_signal_clears_cmax_annualized_value_when_cmax_annualized_false(self):
        """Signal should clear cmax_annualized_value when cmax_annualized is explicitly False."""
        # For tariff not in RULE_2, but with cmax_annualized=False
        contract = BiomethaneContract.objects.create(
            producer=self.producer_entity,
            buyer=self.buyer_entity,
            tariff_reference="2011",
            installation_category=BiomethaneContract.INSTALLATION_CATEGORY_1,
            cmax=150.0,
            cmax_annualized=False,  # Explicitly False
            cmax_annualized_value=100.0,  # This should be cleared
            pap_contracted=25.0,
        )

        contract.refresh_from_db()
        self.assertIsNone(contract.cmax_annualized_value)
        # Other fields should remain
        self.assertEqual(contract.cmax, 150.0)
        self.assertFalse(contract.cmax_annualized)
        self.assertIsNone(contract.pap_contracted)  # Cleared due to RULE_1

    def test_signal_no_clearing_for_unknown_tariff(self):
        """Signal should not clear any fields for unknown tariff references."""
        contract = BiomethaneContract.objects.create(
            producer=self.producer_entity,
            buyer=self.buyer_entity,
            tariff_reference=None,
            installation_category=BiomethaneContract.INSTALLATION_CATEGORY_1,
            cmax=150.0,
            cmax_annualized=True,
            cmax_annualized_value=100.0,
            pap_contracted=25.0,
        )

        contract.refresh_from_db()
        # All fields should remain unchanged
        self.assertEqual(contract.cmax, 150.0)
        self.assertTrue(contract.cmax_annualized)
        self.assertEqual(contract.cmax_annualized_value, 100.0)
        self.assertEqual(contract.pap_contracted, 25.0)

    def test_signal_on_contract_update(self):
        """Signal should trigger on contract updates."""
        # Create initial contract with tariff 2011
        contract = BiomethaneContract.objects.create(
            producer=self.producer_entity,
            buyer=self.buyer_entity,
            tariff_reference="2011",
            installation_category=BiomethaneContract.INSTALLATION_CATEGORY_1,
            cmax=150.0,
            cmax_annualized=True,
            cmax_annualized_value=100.0,
            pap_contracted=25.0,
        )

        contract.refresh_from_db()
        self.assertIsNone(contract.pap_contracted)  # Cleared by RULE_1

        # Update to tariff 2021 - should trigger different clearing rules
        contract.tariff_reference = "2021"
        contract.pap_contracted = 30.0  # Set new value
        contract.save()

        contract.refresh_from_db()
        # Now RULE_2 should apply
        self.assertIsNone(contract.cmax)
        self.assertFalse(contract.cmax_annualized)
        self.assertIsNone(contract.cmax_annualized_value)
        self.assertEqual(contract.pap_contracted, 30.0)  # Should remain

    def test_signal_does_not_clear_already_none_fields(self):
        """Signal should handle None fields gracefully."""
        contract = BiomethaneContract.objects.create(
            producer=self.producer_entity,
            buyer=self.buyer_entity,
            tariff_reference="2021",
            cmax=None,  # Already None
            cmax_annualized=False,  # Will be set to False
            cmax_annualized_value=None,  # Already None
            pap_contracted=25.0,
        )

        contract.refresh_from_db()
        self.assertIsNone(contract.cmax)
        self.assertFalse(contract.cmax_annualized)
        self.assertIsNone(contract.cmax_annualized_value)
        self.assertEqual(contract.pap_contracted, 25.0)

    def test_signal_cmax_annualized_special_case_in_rule_2(self):
        """Signal should handle the special case where cmax_annualized is set to False in RULE_2."""
        contract = BiomethaneContract.objects.create(
            producer=self.producer_entity,
            buyer=self.buyer_entity,
            tariff_reference="2021",
            cmax=150.0,
            cmax_annualized=True,
            cmax_annualized_value=100.0,
            pap_contracted=25.0,
        )

        contract.refresh_from_db()
        # In RULE_2, cmax_annualized should be set to False (not None)
        self.assertFalse(contract.cmax_annualized)
        self.assertIsNone(contract.cmax)
        self.assertIsNone(contract.cmax_annualized_value)
