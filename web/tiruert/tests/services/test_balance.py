from unittest.mock import Mock, patch

from django.test import TestCase

from core.models import MatierePremiere
from tiruert.models import Operation
from tiruert.services.balance import BalanceService


class BalanceServiceDefineConversionFactorTest(TestCase):
    """Unit tests for BalanceService._define_conversion_factor() method."""

    def test_define_conversion_factor_returns_pci_litre_for_mj(self):
        """Test _define_conversion_factor returns 'pci_litre' for 'mj' unit."""
        result = BalanceService._define_conversion_factor("mj")
        self.assertEqual(result, "pci_litre")

    def test_define_conversion_factor_returns_masse_volumique_for_kg(self):
        """Test _define_conversion_factor returns 'masse_volumique' for 'kg' unit."""
        result = BalanceService._define_conversion_factor("kg")
        self.assertEqual(result, "masse_volumique")

    def test_define_conversion_factor_returns_none_for_unknown_unit(self):
        """Test _define_conversion_factor returns None for unknown units."""
        result = BalanceService._define_conversion_factor("liters")
        self.assertIsNone(result)

    def test_define_conversion_factor_returns_none_for_empty_string(self):
        """Test _define_conversion_factor returns None for empty string."""
        result = BalanceService._define_conversion_factor("")
        self.assertIsNone(result)


class BalanceServiceGetConversionFactorTest(TestCase):
    """Unit tests for BalanceService._get_conversion_factor() method."""

    def test_get_conversion_factor_returns_pci_litre_for_mj_unit(self):
        """Test _get_conversion_factor returns pci_litre value for 'mj' unit."""
        mock_biofuel = Mock()
        mock_biofuel.pci_litre = 35.5
        mock_operation = Mock()
        mock_operation.biofuel = mock_biofuel

        result = BalanceService._get_conversion_factor(mock_operation, "mj")

        self.assertEqual(result, 35.5)

    def test_get_conversion_factor_returns_masse_volumique_for_kg_unit(self):
        """Test _get_conversion_factor returns masse_volumique value for 'kg' unit."""
        mock_biofuel = Mock()
        mock_biofuel.masse_volumique = 0.85
        mock_operation = Mock()
        mock_operation.biofuel = mock_biofuel

        result = BalanceService._get_conversion_factor(mock_operation, "kg")

        self.assertEqual(result, 0.85)

    def test_get_conversion_factor_returns_1_for_unknown_unit(self):
        """Test _get_conversion_factor returns 1 for unknown units (no conversion)."""
        mock_operation = Mock()
        mock_operation.biofuel = Mock()

        result = BalanceService._get_conversion_factor(mock_operation, "liters")

        self.assertEqual(result, 1)

    def test_get_conversion_factor_returns_1_when_attribute_missing(self):
        """Test _get_conversion_factor returns 1 when biofuel lacks conversion attribute."""
        mock_biofuel = Mock(spec=[])  # Mock without pci_litre or masse_volumique
        mock_operation = Mock()
        mock_operation.biofuel = mock_biofuel

        result = BalanceService._get_conversion_factor(mock_operation, "mj")

        self.assertEqual(result, 1)


class BalanceServiceInitBalanceEntryTest(TestCase):
    """Unit tests for BalanceService._init_balance_entry() method."""

    def test_init_balance_entry_with_no_operation(self):
        """Test _init_balance_entry creates entry with None values when no operation provided."""
        result = BalanceService._init_balance_entry("mj")

        self.assertIsNone(result["sector"])
        self.assertIsNone(result["customs_category"])
        self.assertIsNone(result["biofuel"])
        self.assertEqual(result["unit"], "mj")
        self.assertEqual(result["quantity"], {"credit": 0, "debit": 0})
        self.assertEqual(result["pending_teneur"], 0)
        self.assertEqual(result["declared_teneur"], 0)
        self.assertEqual(result["available_balance"], 0)
        self.assertEqual(result["saved_emissions"], 0)

    def test_init_balance_entry_with_operation(self):
        """Test _init_balance_entry populates sector, category, biofuel from operation."""
        mock_operation = Mock()
        mock_operation.sector = "ESSENCE"
        mock_operation.customs_category = MatierePremiere.CONV
        mock_operation.biofuel = Mock(code="ETH")

        result = BalanceService._init_balance_entry("mj", operation=mock_operation)

        self.assertEqual(result["sector"], "ESSENCE")
        self.assertEqual(result["customs_category"], MatierePremiere.CONV)
        self.assertEqual(result["biofuel"], mock_operation.biofuel)
        self.assertEqual(result["unit"], "mj")


class BalanceServiceGetKeyTest(TestCase):
    """Unit tests for BalanceService._get_key() method."""

    def test_get_key_returns_sector_when_group_by_sector(self):
        """Test _get_key returns operation.sector when grouping by sector."""
        mock_operation = Mock()
        mock_operation.sector = "ESSENCE"

        result = BalanceService._get_key(mock_operation, BalanceService.GROUP_BY_SECTOR)

        self.assertEqual(result, "ESSENCE")

    def test_get_key_returns_category_when_group_by_category(self):
        """Test _get_key returns operation.customs_category when grouping by category."""
        mock_operation = Mock()
        mock_operation.customs_category = MatierePremiere.CONV

        result = BalanceService._get_key(mock_operation, BalanceService.GROUP_BY_CATEGORY)

        self.assertEqual(result, MatierePremiere.CONV)

    def test_get_key_returns_base_tuple_for_default_grouping(self):
        """Test _get_key returns (sector, category, biofuel_code) for other groupings."""
        mock_operation = Mock()
        mock_operation.sector = "ESSENCE"
        mock_operation.customs_category = MatierePremiere.CONV
        mock_operation.biofuel.code = "ETH"

        result = BalanceService._get_key(mock_operation, "other")

        self.assertEqual(result, ("ESSENCE", MatierePremiere.CONV, "ETH"))

    def test_get_key_adds_lot_id_when_group_by_lot(self):
        """Test _get_key adds lot.id to tuple when grouping by lot."""
        mock_operation = Mock()
        mock_operation.sector = "ESSENCE"
        mock_operation.customs_category = MatierePremiere.CONV
        mock_operation.biofuel.code = "ETH"
        mock_detail = Mock()
        mock_detail.lot.id = 123

        result = BalanceService._get_key(mock_operation, BalanceService.GROUP_BY_LOT, detail=mock_detail)

        self.assertEqual(result, ("ESSENCE", MatierePremiere.CONV, "ETH", 123))

    def test_get_key_adds_depot_when_group_by_depot(self):
        """Test _get_key adds depot to tuple when grouping by depot."""
        mock_operation = Mock()
        mock_operation.sector = "ESSENCE"
        mock_operation.customs_category = MatierePremiere.CONV
        mock_operation.biofuel.code = "ETH"
        mock_depot = Mock(name="Depot A")

        result = BalanceService._get_key(mock_operation, BalanceService.GROUP_BY_DEPOT, depot=mock_depot)

        self.assertEqual(result, ("ESSENCE", MatierePremiere.CONV, "ETH", mock_depot))

    def test_get_key_returns_base_tuple_when_lot_grouping_without_detail(self):
        """Test _get_key returns base tuple when grouping by lot but detail is None."""
        mock_operation = Mock()
        mock_operation.sector = "ESSENCE"
        mock_operation.customs_category = MatierePremiere.CONV
        mock_operation.biofuel.code = "ETH"

        result = BalanceService._get_key(mock_operation, BalanceService.GROUP_BY_LOT, detail=None)

        self.assertEqual(result, ("ESSENCE", MatierePremiere.CONV, "ETH"))


class BalanceServiceCalculateQuantityTest(TestCase):
    """Unit tests for BalanceService.calculate_quantity() method."""

    def test_calculate_quantity_multiplies_all_factors(self):
        """Test calculate_quantity multiplies volume * conversion_factor * renewable_energy_share."""
        mock_operation = Mock()
        mock_operation.renewable_energy_share = 0.8
        mock_detail = Mock()
        mock_detail.volume = 100.0
        conversion_factor = 2.5

        result = BalanceService._calculate_quantity(mock_operation, mock_detail, conversion_factor)

        self.assertEqual(result, 200.0)  # 100 * 2.5 * 0.8 = 200


class BalanceServiceUpdateQuantityAndTeneurTest(TestCase):
    """Unit tests for BalanceService._update_quantity_and_teneur() method."""

    def test_update_quantity_and_teneur_adds_to_credit_quantity(self):
        """Test _update_quantity_and_teneur adds volume to credit when credit_operation=True."""
        balance = {"key1": {"quantity": {"credit": 10.0, "debit": 5.0}, "pending_teneur": 0, "declared_teneur": 0}}
        mock_operation = Mock()
        mock_operation.type = Operation.CESSION
        mock_operation.renewable_energy_share = 1.0
        mock_detail = Mock()
        mock_detail.volume = 20.0

        BalanceService._update_quantity_and_teneur(balance, "key1", mock_operation, mock_detail, True, 1.0)

        self.assertEqual(balance["key1"]["quantity"]["credit"], 30.0)
        self.assertEqual(balance["key1"]["quantity"]["debit"], 5.0)

    def test_update_quantity_and_teneur_adds_to_debit_quantity(self):
        """Test _update_quantity_and_teneur adds volume to debit when credit_operation=False."""
        balance = {"key1": {"quantity": {"credit": 10.0, "debit": 5.0}, "pending_teneur": 0, "declared_teneur": 0}}
        mock_operation = Mock()
        mock_operation.type = Operation.CESSION
        mock_operation.renewable_energy_share = 1.0
        mock_detail = Mock()
        mock_detail.volume = 15.0

        BalanceService._update_quantity_and_teneur(balance, "key1", mock_operation, mock_detail, False, 1.0)

        self.assertEqual(balance["key1"]["quantity"]["credit"], 10.0)
        self.assertEqual(balance["key1"]["quantity"]["debit"], 20.0)

    def test_update_quantity_and_teneur_updates_pending_teneur_for_pending_teneur_operation(self):
        """Test _update_quantity_and_teneur updates pending_teneur for PENDING TENEUR operations."""
        balance = {"key1": {"quantity": {"credit": 0.0, "debit": 0.0}, "pending_teneur": 5.0, "declared_teneur": 0.0}}
        mock_operation = Mock()
        mock_operation.type = Operation.TENEUR
        mock_operation.status = Operation.PENDING
        mock_operation.renewable_energy_share = 1.0
        mock_detail = Mock()
        mock_detail.volume = 10.0

        BalanceService._update_quantity_and_teneur(balance, "key1", mock_operation, mock_detail, True, 1.0)

        self.assertEqual(balance["key1"]["pending_teneur"], 15.0)
        self.assertEqual(balance["key1"]["declared_teneur"], 0.0)

    def test_update_quantity_and_teneur_updates_declared_teneur_for_non_pending_teneur_operation(self):
        """Test _update_quantity_and_teneur updates declared_teneur for DECLARED/VALIDATED TENEUR operations."""
        balance = {"key1": {"quantity": {"credit": 0.0, "debit": 0.0}, "pending_teneur": 0.0, "declared_teneur": 3.0}}
        mock_operation = Mock()
        mock_operation.type = Operation.TENEUR
        mock_operation.status = Operation.DECLARED
        mock_operation.renewable_energy_share = 1.0
        mock_detail = Mock()
        mock_detail.volume = 7.0

        BalanceService._update_quantity_and_teneur(balance, "key1", mock_operation, mock_detail, True, 1.0)

        self.assertEqual(balance["key1"]["pending_teneur"], 0.0)
        self.assertEqual(balance["key1"]["declared_teneur"], 10.0)

    def test_update_quantity_and_teneur_rounds_to_2_decimals(self):
        """Test _update_quantity_and_teneur rounds results to 2 decimal places."""
        balance = {"key1": {"quantity": {"credit": 0.0, "debit": 0.0}, "pending_teneur": 0.0, "declared_teneur": 0.0}}
        mock_operation = Mock()
        mock_operation.type = Operation.CESSION
        mock_operation.renewable_energy_share = 0.333
        mock_detail = Mock()
        mock_detail.volume = 10.0

        BalanceService._update_quantity_and_teneur(balance, "key1", mock_operation, mock_detail, True, 1.0)

        self.assertEqual(balance["key1"]["quantity"]["credit"], 3.33)


class BalanceServiceUpdateAvailableBalanceTest(TestCase):
    """Unit tests for BalanceService._update_available_balance() method."""

    @patch("tiruert.services.teneur.TeneurService.convert_producted_emissions_to_avoided_emissions")
    def test_update_available_balance_adds_volume_for_credit_operation(self, mock_convert):
        """Test _update_available_balance adds volume when credit_operation=True."""
        mock_convert.return_value = 50.0
        balance = {"key1": {"available_balance": 100.0, "saved_emissions": 0.0, "emission_rate_per_mj": 0}}
        mock_operation = Mock()
        mock_operation.biofuel = Mock()
        mock_operation.renewable_energy_share = 1.0
        mock_detail = Mock()
        mock_detail.volume = 20.0
        mock_detail.emission_rate_per_mj = 25.0

        BalanceService._update_available_balance(balance, "key1", mock_operation, mock_detail, True, 1.0)

        self.assertEqual(balance["key1"]["available_balance"], 120.0)
        self.assertEqual(balance["key1"]["saved_emissions"], 50.0)

    @patch("tiruert.services.teneur.TeneurService.convert_producted_emissions_to_avoided_emissions")
    def test_update_available_balance_subtracts_volume_for_debit_operation(self, mock_convert):
        """Test _update_available_balance subtracts volume when credit_operation=False."""
        mock_convert.return_value = 30.0
        balance = {"key1": {"available_balance": 100.0, "saved_emissions": 0.0, "emission_rate_per_mj": 0}}
        mock_operation = Mock()
        mock_operation.biofuel = Mock()
        mock_operation.renewable_energy_share = 1.0
        mock_detail = Mock()
        mock_detail.volume = 15.0
        mock_detail.emission_rate_per_mj = 20.0

        BalanceService._update_available_balance(balance, "key1", mock_operation, mock_detail, False, 1.0)

        self.assertEqual(balance["key1"]["available_balance"], 85.0)
        self.assertEqual(balance["key1"]["saved_emissions"], -30.0)

    @patch("tiruert.services.teneur.TeneurService.convert_producted_emissions_to_avoided_emissions")
    def test_update_available_balance_sets_emission_rate(self, mock_convert):
        """Test _update_available_balance sets emission_rate_per_mj from detail."""
        mock_convert.return_value = 0.0
        balance = {"key1": {"available_balance": 0.0, "saved_emissions": 0.0, "emission_rate_per_mj": 0}}
        mock_operation = Mock()
        mock_operation.biofuel = Mock()
        mock_operation.renewable_energy_share = 1.0
        mock_detail = Mock()
        mock_detail.volume = 10.0
        mock_detail.emission_rate_per_mj = 42.5

        BalanceService._update_available_balance(balance, "key1", mock_operation, mock_detail, True, 1.0)

        self.assertEqual(balance["key1"]["emission_rate_per_mj"], 42.5)

    @patch("tiruert.services.teneur.TeneurService.convert_producted_emissions_to_avoided_emissions")
    def test_update_available_balance_rounds_to_2_decimals(self, mock_convert):
        """Test _update_available_balance rounds results to 2 decimal places."""
        mock_convert.return_value = 12.3456
        balance = {"key1": {"available_balance": 0.0, "saved_emissions": 0.0, "emission_rate_per_mj": 0}}
        mock_operation = Mock()
        mock_operation.biofuel = Mock()
        mock_operation.renewable_energy_share = 0.333
        mock_detail = Mock()
        mock_detail.volume = 10.0
        mock_detail.emission_rate_per_mj = 25.0

        BalanceService._update_available_balance(balance, "key1", mock_operation, mock_detail, True, 1.0)

        self.assertEqual(balance["key1"]["available_balance"], 3.33)
        self.assertEqual(balance["key1"]["saved_emissions"], 12.35)


class BalanceServiceUpdateGhgMinMaxTest(TestCase):
    """Unit tests for BalanceService._update_ghg_min_max() method."""

    def test_update_ghg_min_max_sets_initial_min_and_max(self):
        """Test _update_ghg_min_max sets min and max when both are None."""
        balance = {"key1": {"ghg_reduction_min": None, "ghg_reduction_max": None}}
        mock_detail = Mock()
        mock_detail.lot.ghg_reduction_red_ii = 65.5

        BalanceService._update_ghg_min_max(balance, "key1", mock_detail)

        self.assertEqual(balance["key1"]["ghg_reduction_min"], 65.5)
        self.assertEqual(balance["key1"]["ghg_reduction_max"], 65.5)

    def test_update_ghg_min_max_updates_min_when_new_value_is_lower(self):
        """Test _update_ghg_min_max updates min when new value is lower than current."""
        balance = {"key1": {"ghg_reduction_min": 70.0, "ghg_reduction_max": 80.0}}
        mock_detail = Mock()
        mock_detail.lot.ghg_reduction_red_ii = 60.0

        BalanceService._update_ghg_min_max(balance, "key1", mock_detail)

        self.assertEqual(balance["key1"]["ghg_reduction_min"], 60.0)
        self.assertEqual(balance["key1"]["ghg_reduction_max"], 80.0)

    def test_update_ghg_min_max_updates_max_when_new_value_is_higher(self):
        """Test _update_ghg_min_max updates max when new value is higher than current."""
        balance = {"key1": {"ghg_reduction_min": 60.0, "ghg_reduction_max": 70.0}}
        mock_detail = Mock()
        mock_detail.lot.ghg_reduction_red_ii = 85.0

        BalanceService._update_ghg_min_max(balance, "key1", mock_detail)

        self.assertEqual(balance["key1"]["ghg_reduction_min"], 60.0)
        self.assertEqual(balance["key1"]["ghg_reduction_max"], 85.0)

    def test_update_ghg_min_max_keeps_existing_when_new_value_is_between(self):
        """Test _update_ghg_min_max keeps existing min/max when new value is between them."""
        balance = {"key1": {"ghg_reduction_min": 60.0, "ghg_reduction_max": 80.0}}
        mock_detail = Mock()
        mock_detail.lot.ghg_reduction_red_ii = 70.0

        BalanceService._update_ghg_min_max(balance, "key1", mock_detail)

        self.assertEqual(balance["key1"]["ghg_reduction_min"], 60.0)
        self.assertEqual(balance["key1"]["ghg_reduction_max"], 80.0)


class BalanceServiceCalculateBalanceIntegrationTest(TestCase):
    """Integration tests for BalanceService.calculate_balance() method."""

    fixtures = [
        "json/biofuels.json",
        "json/feedstock.json",
        "json/countries.json",
        "json/entities.json",
        "json/productionsites.json",
    ]

    def setUp(self):
        from core.models import Entity
        from tiruert.factories import OperationDetailFactory, OperationFactory

        self.entity, _ = Entity.objects.get_or_create(
            name="Test Entity",
            entity_type=Entity.OPERATOR,
        )
        self.OperationFactory = OperationFactory
        self.OperationDetailFactory = OperationDetailFactory

    def _create_operation_with_details(self, **op_kwargs):
        """Helper to create an operation with details."""
        op = self.OperationFactory(**op_kwargs)
        self.OperationDetailFactory.create_for_operation(op)
        return op

    @patch("tiruert.services.teneur.TeneurService.convert_producted_emissions_to_avoided_emissions")
    def test_calculate_balance_groups_operations_by_sector(self, mock_convert):
        """Test calculate_balance correctly groups operations by sector."""
        from core.models import Biocarburant

        mock_convert.return_value = 0.0

        # Get biofuels from different sectors
        biofuel_essence = Biocarburant.objects.filter(compatible_essence=True).first()
        biofuel_diesel = Biocarburant.objects.filter(compatible_diesel=True).first()

        # Skip test if we don't have biofuels for different sectors
        if not biofuel_essence or not biofuel_diesel:
            self.skipTest("Missing biofuels for different sectors in fixtures")

        # Create 3 operations: 2 with essence, 1 with diesel
        # If grouping works correctly, we should have 2 groups (not 3)
        op_essence_1 = self._create_operation_with_details(
            debited_entity=self.entity,
            type=Operation.CESSION,
            status=Operation.VALIDATED,
            biofuel=biofuel_essence,
        )
        op_essence_2 = self._create_operation_with_details(
            debited_entity=self.entity,
            type=Operation.CESSION,
            status=Operation.VALIDATED,
            biofuel=biofuel_essence,
        )
        op_diesel = self._create_operation_with_details(
            debited_entity=self.entity,
            type=Operation.CESSION,
            status=Operation.VALIDATED,
            biofuel=biofuel_diesel,
        )

        operations = Operation.objects.filter(id__in=[op_essence_1.id, op_essence_2.id, op_diesel.id])

        result = BalanceService.calculate_balance(operations, self.entity.id, BalanceService.GROUP_BY_SECTOR, "l")

        # Should have exactly 2 sectors (ESSENCE and GAZOLE), not 3
        # This proves that op_essence_1 and op_essence_2 are grouped together
        self.assertEqual(len(result), 2)
        self.assertIn(Operation.ESSENCE, result)
        self.assertIn(Operation.GAZOLE, result)

        # Essence sector should have combined quantity from both operations
        # Each detail has a random volume (100-5000), so we just check > 0
        self.assertGreater(result[Operation.ESSENCE]["quantity"]["debit"], 0)
        self.assertGreater(result[Operation.GAZOLE]["quantity"]["debit"], 0)

    @patch("tiruert.services.teneur.TeneurService.convert_producted_emissions_to_avoided_emissions")
    def test_calculate_balance_filters_operations_by_status(self, mock_convert):
        """Test calculate_balance only includes operations with allowed statuses."""
        mock_convert.return_value = 0.0

        # Allowed statuses according to calculate_balance implementation
        allowed_statuses = [
            Operation.PENDING,
            Operation.ACCEPTED,
            Operation.VALIDATED,
            Operation.DECLARED,
            Operation.DRAFT,
        ]

        for status_code, _ in Operation.OPERATION_STATUSES:
            with self.subTest(status=status_code):
                # Create operation with specific status
                op = self._create_operation_with_details(
                    debited_entity=self.entity,
                    type=Operation.CESSION,
                    status=status_code,
                )

                operations = Operation.objects.filter(id=op.id)

                result = BalanceService.calculate_balance(operations, self.entity.id, BalanceService.GROUP_BY_SECTOR, "l")

                if status_code in allowed_statuses:
                    # Should have at least one entry with quantity > 0
                    self.assertGreater(len(result), 0)
                    has_quantity = any(
                        entry["quantity"]["debit"] > 0 or entry["quantity"]["credit"] > 0 for entry in result.values()
                    )
                    self.assertTrue(has_quantity, f"Status {status_code} should contribute to balance")
                else:
                    # Should be filtered out - no quantities or empty result
                    if len(result) > 0:
                        for entry in result.values():
                            self.assertEqual(
                                entry["quantity"]["debit"], 0, f"Status {status_code} should not contribute to debit"
                            )
                            self.assertEqual(
                                entry["quantity"]["credit"], 0, f"Status {status_code} should not contribute to credit"
                            )

    @patch("tiruert.services.teneur.TeneurService.convert_producted_emissions_to_avoided_emissions")
    def test_calculate_balance_applies_credit_and_debit_logic(self, mock_convert):
        """Test calculate_balance correctly applies credit/debit based on entity relationship."""
        mock_convert.return_value = 0.0

        # Credit operation (entity receives)
        op_credit = self._create_operation_with_details(
            credited_entity=self.entity,
            type=Operation.CESSION,
            status=Operation.VALIDATED,
        )
        # Debit operation (entity gives)
        op_debit = self._create_operation_with_details(
            debited_entity=self.entity,
            type=Operation.CESSION,
            status=Operation.VALIDATED,
        )

        operations = Operation.objects.filter(id__in=[op_credit.id, op_debit.id])

        result = BalanceService.calculate_balance(operations, self.entity.id, BalanceService.GROUP_BY_SECTOR, "l")

        # Should have at least one balance entry
        self.assertGreater(len(result), 0)

        # Check that at least one entry has credit or debit
        has_credit_or_debit = any(
            entry["quantity"]["credit"] > 0 or entry["quantity"]["debit"] > 0 for entry in result.values()
        )
        self.assertTrue(has_credit_or_debit)

    @patch("tiruert.services.teneur.TeneurService.convert_producted_emissions_to_avoided_emissions")
    def test_calculate_balance_excludes_pending_credits_from_available_balance(self, mock_convert):
        """Test calculate_balance excludes PENDING credit operations from available_balance."""
        mock_convert.return_value = 0.0

        op_pending = self._create_operation_with_details(
            credited_entity=self.entity,
            type=Operation.CESSION,
            status=Operation.PENDING,
        )

        operations = Operation.objects.filter(id=op_pending.id)

        result = BalanceService.calculate_balance(operations, self.entity.id, BalanceService.GROUP_BY_SECTOR, "l")

        # Pending credit operations should not update available_balance
        for entry in result.values():
            self.assertEqual(entry["available_balance"], 0)

    @patch("tiruert.services.teneur.TeneurService.convert_producted_emissions_to_avoided_emissions")
    def test_calculate_balance_applies_ges_filtering(self, mock_convert):
        """Test calculate_balance filters lots by GHG reduction bounds."""
        mock_convert.return_value = 0.0

        # Operation with high GHG reduction
        op = self._create_operation_with_details(
            debited_entity=self.entity,
            type=Operation.CESSION,
            status=Operation.VALIDATED,
        )
        # Set GHG reduction on all lots
        for detail in op.details.all():
            detail.lot.ghg_reduction_red_ii = 80.0
            detail.lot.save()

        operations = Operation.objects.filter(id=op.id)

        # Filter to exclude high GHG (keep only 50-70%)
        result = BalanceService.calculate_balance(
            operations, self.entity.id, BalanceService.GROUP_BY_SECTOR, "liters", ges_bound_min=50.0, ges_bound_max=70.0
        )

        # Operations should be excluded, so all quantities should be 0
        for entry in result.values():
            self.assertEqual(entry["quantity"]["debit"], 0)
            self.assertEqual(entry["quantity"]["credit"], 0)

    @patch("tiruert.services.teneur.TeneurService.convert_producted_emissions_to_avoided_emissions")
    def test_calculate_balance_respects_date_from_filter(self, mock_convert):
        """Test calculate_balance filters quantity updates by date_from."""
        from datetime import datetime, timezone

        mock_convert.return_value = 0.0

        # Create operation with specific date
        op = self._create_operation_with_details(
            debited_entity=self.entity,
            type=Operation.CESSION,
            status=Operation.VALIDATED,
        )
        # Set created_at to past date
        op.created_at = datetime(2024, 1, 1, tzinfo=timezone.utc)
        op.save()

        operations = Operation.objects.filter(id=op.id)

        # Request balance with date_from after operation date
        result = BalanceService.calculate_balance(
            operations,
            self.entity.id,
            BalanceService.GROUP_BY_SECTOR,
            "liters",
            date_from=datetime(2024, 6, 1, tzinfo=timezone.utc),
        )

        # Quantity should not be updated (date_from filter)
        for entry in result.values():
            self.assertEqual(entry["quantity"]["debit"], 0)

    @patch("tiruert.services.teneur.TeneurService.convert_producted_emissions_to_avoided_emissions")
    def test_calculate_balance_groups_by_category(self, mock_convert):
        """Test calculate_balance groups by customs_category correctly."""
        mock_convert.return_value = 0.0

        op1 = self._create_operation_with_details(
            debited_entity=self.entity,
            type=Operation.CESSION,
            status=Operation.VALIDATED,
        )

        operations = Operation.objects.filter(id=op1.id)

        result = BalanceService.calculate_balance(operations, self.entity.id, BalanceService.GROUP_BY_CATEGORY, "liters")

        # Should have at least one customs_category group
        self.assertGreater(len(result), 0)

        # Verify that keys are customs_category values
        for key in result.keys():
            self.assertIsInstance(key, str)  # customs_category is a string

    @patch("tiruert.services.teneur.TeneurService.convert_producted_emissions_to_avoided_emissions")
    def test_calculate_balance_updates_teneur_by_status(self, mock_convert):
        """Test calculate_balance updates pending_teneur vs declared_teneur based on operation status."""
        mock_convert.return_value = 0.0

        op_pending = self._create_operation_with_details(
            debited_entity=self.entity,
            type=Operation.TENEUR,
            status=Operation.PENDING,
        )
        op_declared = self._create_operation_with_details(
            debited_entity=self.entity,
            type=Operation.TENEUR,
            status=Operation.DECLARED,
        )

        operations = Operation.objects.filter(id__in=[op_pending.id, op_declared.id])

        result = BalanceService.calculate_balance(operations, self.entity.id, BalanceService.GROUP_BY_SECTOR, "liters")

        # At least one entry should have teneur values
        has_pending_teneur = any(entry["pending_teneur"] > 0 for entry in result.values())
        has_declared_teneur = any(entry["declared_teneur"] > 0 for entry in result.values())

        self.assertTrue(has_pending_teneur or has_declared_teneur)

    @patch("tiruert.services.teneur.TeneurService.convert_producted_emissions_to_avoided_emissions")
    def test_calculate_balance_applies_conversion_factor_for_mj(self, mock_convert):
        """Test calculate_balance applies conversion factor when unit is 'mj'."""
        mock_convert.return_value = 0.0

        op = self._create_operation_with_details(
            debited_entity=self.entity,
            type=Operation.CESSION,
            status=Operation.VALIDATED,
        )

        operations = Operation.objects.filter(id=op.id)

        # Get balance in MJ (with conversion)
        result_mj = BalanceService.calculate_balance(operations, self.entity.id, BalanceService.GROUP_BY_SECTOR, "mj")

        # Should have results and unit should be 'mj'
        self.assertGreater(len(result_mj), 0)
        sector_key = op.sector
        self.assertIn(sector_key, result_mj)
        self.assertEqual(result_mj[sector_key]["unit"], "mj")

        # Should have non-zero quantity (conversion applied successfully)
        self.assertGreater(result_mj[sector_key]["quantity"]["debit"], 0)
