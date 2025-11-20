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
        result = BalanceService._init_balance_entry("liters")

        self.assertIsNone(result["sector"])
        self.assertIsNone(result["customs_category"])
        self.assertIsNone(result["biofuel"])
        self.assertEqual(result["unit"], "liters")
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

    def test_init_balance_entry_initializes_all_required_fields(self):
        """Test _init_balance_entry initializes all required balance fields."""
        result = BalanceService._init_balance_entry("kg")

        expected_keys = [
            "sector",
            "customs_category",
            "biofuel",
            "quantity",
            "emission_rate_per_mj",
            "pending_teneur",
            "pending_operations",
            "declared_teneur",
            "available_balance",
            "unit",
            "ghg_reduction_min",
            "ghg_reduction_max",
            "saved_emissions",
        ]

        for key in expected_keys:
            self.assertIn(key, result, f"Missing key: {key}")


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

    def test_update_quantity_and_teneur_applies_conversion_factor(self):
        """Test _update_quantity_and_teneur applies conversion factor to volume."""
        balance = {"key1": {"quantity": {"credit": 0.0, "debit": 0.0}, "pending_teneur": 0, "declared_teneur": 0}}
        mock_operation = Mock()
        mock_operation.type = Operation.CESSION
        mock_operation.renewable_energy_share = 1.0
        mock_detail = Mock()
        mock_detail.volume = 10.0

        BalanceService._update_quantity_and_teneur(balance, "key1", mock_operation, mock_detail, True, 2.5)

        self.assertEqual(balance["key1"]["quantity"]["credit"], 25.0)

    def test_update_quantity_and_teneur_applies_renewable_energy_share(self):
        """Test _update_quantity_and_teneur applies renewable_energy_share to quantity."""
        balance = {"key1": {"quantity": {"credit": 0.0, "debit": 0.0}, "pending_teneur": 0, "declared_teneur": 0}}
        mock_operation = Mock()
        mock_operation.type = Operation.CESSION
        mock_operation.renewable_energy_share = 0.5
        mock_detail = Mock()
        mock_detail.volume = 100.0

        BalanceService._update_quantity_and_teneur(balance, "key1", mock_operation, mock_detail, True, 1.0)

        self.assertEqual(balance["key1"]["quantity"]["credit"], 50.0)

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
    def test_update_available_balance_applies_conversion_factor(self, mock_convert):
        """Test _update_available_balance applies conversion factor to volume."""
        mock_convert.return_value = 100.0
        balance = {"key1": {"available_balance": 0.0, "saved_emissions": 0.0, "emission_rate_per_mj": 0}}
        mock_operation = Mock()
        mock_operation.biofuel = Mock()
        mock_operation.renewable_energy_share = 1.0
        mock_detail = Mock()
        mock_detail.volume = 10.0
        mock_detail.emission_rate_per_mj = 30.0

        BalanceService._update_available_balance(balance, "key1", mock_operation, mock_detail, True, 3.0)

        self.assertEqual(balance["key1"]["available_balance"], 30.0)

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
