from unittest.mock import Mock, patch

import numpy as np
from django.test import SimpleTestCase, TestCase

from tiruert.models import Operation
from tiruert.services.teneur import TeneurService, TeneurServiceErrors


class TeneurServiceOptimizeBiofuelBlendingTest(SimpleTestCase):
    """Test TeneurService.optimize_biofuel_blending() method"""

    def test_optimize_biofuel_blending_successful_optimization(self):
        """Test successful optimization with valid inputs"""
        batches_volumes = np.array([100.0, 150.0, 200.0])
        batches_emissions = np.array([50.0, 60.0, 70.0])
        target_volume = 250.0
        target_emission = 60.0  # Within range of available emissions

        selected_batches, fun = TeneurService.optimize_biofuel_blending(
            batches_volumes, batches_emissions, target_volume, target_emission
        )

        self.assertIsInstance(selected_batches, dict)
        self.assertIsInstance(fun, float)

        total_volume = sum(selected_batches.values())
        self.assertEqual(total_volume, target_volume)

        selected_indices = np.array(list(selected_batches.keys()), dtype=np.int64)
        selected_volumes = np.array(list(selected_batches.values()), dtype=np.float64)
        achieved_emission = float(np.dot(selected_volumes, batches_emissions[selected_indices]) / selected_volumes.sum())
        self.assertLessEqual(achieved_emission, target_emission + 1e-9)

    def test_optimize_biofuel_blending_with_enforced_volumes(self):
        """Test optimization with enforced volumes for specific batches"""
        batches_volumes = np.array([100.0, 150.0, 200.0])
        batches_emissions = np.array([50.0, 60.0, 70.0])
        target_volume = 250.0
        target_emission = 62.0  # Within range of available emissions
        enforced_volumes = np.array([50.0, 0.0, 0.0])  # Force 50L from first batch

        selected_batches, fun = TeneurService.optimize_biofuel_blending(
            batches_volumes, batches_emissions, target_volume, target_emission, enforced_volumes
        )

        # Verify first batch has at least the enforced volume
        self.assertIn(0, selected_batches)
        self.assertGreaterEqual(selected_batches[0], 50.0)

    def test_optimize_biofuel_blending_with_max_n_batches(self):
        """Test optimization with maximum number of batches constraint"""
        batches_volumes = np.array([100.0, 150.0, 200.0, 250.0])
        batches_emissions = np.array([50.0, 55.0, 60.0, 65.0])
        target_volume = 300.0
        target_emission = 58.0
        max_n_batches = 2

        selected_batches, fun = TeneurService.optimize_biofuel_blending(
            batches_volumes, batches_emissions, target_volume, target_emission, max_n_batches=max_n_batches
        )

        # Verify number of selected batches respects constraint
        self.assertLessEqual(len(selected_batches), max_n_batches)

    def test_optimize_biofuel_blending_insufficient_volume_raises_error(self):
        """Test that insufficient total volume raises ValueError"""
        batches_volumes = np.array([100.0, 50.0])
        batches_emissions = np.array([50.0, 60.0])
        target_volume = 200.0  # More than available
        target_emission = 55.0

        with self.assertRaises(ValueError) as context:
            TeneurService.optimize_biofuel_blending(batches_volumes, batches_emissions, target_volume, target_emission)

        self.assertEqual(str(context.exception), TeneurServiceErrors.INSUFFICIENT_INPUT_VOLUME)

    def test_optimize_biofuel_blending_enforced_volumes_too_high_raises_error(self):
        """Test that enforced volumes exceeding batch volumes raises ValueError"""
        batches_volumes = np.array([100.0, 150.0])
        batches_emissions = np.array([50.0, 60.0])
        target_volume = 200.0
        target_emission = 55.0
        enforced_volumes = np.array([150.0, 0.0])  # Exceeds first batch volume

        with self.assertRaises(ValueError) as context:
            TeneurService.optimize_biofuel_blending(
                batches_volumes, batches_emissions, target_volume, target_emission, enforced_volumes
            )

        self.assertEqual(str(context.exception), TeneurServiceErrors.ENFORCED_VOLUMES_TOO_HIGH)

    def test_optimize_biofuel_blending_incoherent_max_n_batches_raises_error(self):
        """Test that max_n_batches less than enforced batches count raises ValueError"""
        batches_volumes = np.array([100.0, 150.0, 200.0])
        batches_emissions = np.array([50.0, 60.0, 70.0])
        target_volume = 250.0
        target_emission = 55.0
        enforced_volumes = np.array([50.0, 75.0, 0.0])  # 2 enforced batches
        max_n_batches = 1  # Less than enforced count

        with self.assertRaises(ValueError) as context:
            TeneurService.optimize_biofuel_blending(
                batches_volumes, batches_emissions, target_volume, target_emission, enforced_volumes, max_n_batches
            )

        self.assertEqual(str(context.exception), TeneurServiceErrors.INCOHERENT_ENFORCED_VOLUMES_WITH_MAX_N_BATCHES)

    def test_optimize_biofuel_blending_rounds_volumes_to_2_decimals(self):
        """Test that selected volumes are rounded to 2 decimal places"""
        batches_volumes = np.array([100.123, 150.456, 200.789])
        batches_emissions = np.array([50.0, 60.0, 70.0])
        target_volume = 250.0
        target_emission = 60.0  # Within range of available emissions

        selected_batches, fun = TeneurService.optimize_biofuel_blending(
            batches_volumes, batches_emissions, target_volume, target_emission
        )

        # Verify all volumes have at most 2 decimal places
        for volume in selected_batches.values():
            self.assertEqual(volume, round(volume, 2))

    def test_optimize_biofuel_blending_total_selected_volume_never_exceeds_target(self):
        """Test that selected volumes sum is always lower or equal to target volume precision."""
        batches_volumes = np.array([200.0, 200.0, 200.0])
        batches_emissions = np.array([50.0, 60.0, 70.0])
        target_volume = 450.019
        target_emission = 60.0

        selected_batches, _ = TeneurService.optimize_biofuel_blending(
            batches_volumes, batches_emissions, target_volume, target_emission
        )

        normalized_target_volume = np.floor(target_volume * 100) / 100
        total_selected_volume = sum(selected_batches.values())
        self.assertLessEqual(total_selected_volume, normalized_target_volume)


class TeneurServiceEmissionBoundsTest(SimpleTestCase):
    """Test TeneurService.emission_bounds() method"""

    def test_emission_bounds_returns_min_and_max(self):
        """Test that emission_bounds returns tuple of (min, max) emission rates"""
        batches_volumes = np.array([100.0, 150.0, 200.0])
        batches_emissions = np.array([50.0, 60.0, 70.0])
        target_volume = 250.0

        min_emission, max_emission = TeneurService.emission_bounds(batches_volumes, batches_emissions, target_volume)

        self.assertIsInstance(min_emission, float)
        self.assertIsInstance(max_emission, float)
        self.assertLess(min_emission, max_emission)

    def test_emission_bounds_min_and_max_use_lowest_emissions(self):
        """Test that minimum emission uses batches with lowest emission rates"""
        batches_volumes = np.array([100.0, 100.0, 100.0])
        batches_emissions = np.array([30.0, 60.0, 90.0])
        target_volume = 150.0

        min_emission, max_emission = TeneurService.emission_bounds(batches_volumes, batches_emissions, target_volume)

        # Min should be close to whole of 30 and half of 60
        expected_min = (100 * 30 + 50 * 60) / 150
        self.assertEqual(min_emission, expected_min)

        # Max should be close to whole of 90 and half of 60
        expected_max = (100 * 90 + 50 * 60) / 150
        self.assertEqual(max_emission, expected_max)

    def test_emission_bounds_with_target_volume_equals_sum(self):
        """Test emission_bounds when target volume equals sum of all batches"""
        batches_volumes = np.array([100.0, 150.0, 200.0])
        batches_emissions = np.array([50.0, 60.0, 70.0])
        target_volume = 450.0  # Sum of all volumes

        min_emission, max_emission = TeneurService.emission_bounds(batches_volumes, batches_emissions, target_volume)

        # When using all batches, min and max should be the weighted average
        expected_emission = np.dot(batches_volumes, batches_emissions) / target_volume
        self.assertEqual(min_emission, expected_emission)
        self.assertEqual(max_emission, expected_emission)

    def test_emission_bounds_with_target_volume_equals_truncated_sum(self):
        """Test emission_bounds keeps the last partial batch when the target is truncated."""
        batches_volumes = np.array([100.129, 150.239, 200.349])
        batches_emissions = np.array([50.0, 60.0, 70.0])
        target_volume = batches_volumes.sum()

        min_emission, max_emission = TeneurService.emission_bounds(batches_volumes, batches_emissions, target_volume)

        normalized_target_volume = 450.71
        expected_min = (
            100.129 * 50.0 + 150.239 * 60.0 + (normalized_target_volume - (100.129 + 150.239)) * 70.0
        ) / normalized_target_volume
        expected_max = (
            200.349 * 70.0 + 150.239 * 60.0 + (normalized_target_volume - (200.349 + 150.239)) * 50.0
        ) / normalized_target_volume
        self.assertAlmostEqual(min_emission, expected_min)
        self.assertAlmostEqual(max_emission, expected_max)

    def test_emission_bounds_insufficient_volume_raises_error(self):
        """Test that insufficient volume raises ValueError"""
        batches_volumes = np.array([100.0, 50.0])
        batches_emissions = np.array([50.0, 60.0])
        target_volume = 200.0  # More than available

        with self.assertRaises(ValueError) as context:
            TeneurService.emission_bounds(batches_volumes, batches_emissions, target_volume)

        self.assertEqual(str(context.exception), TeneurServiceErrors.INSUFFICIENT_INPUT_VOLUME)


class TeneurServiceConvertEmissionsTest(SimpleTestCase):
    """Test TeneurService.convert_producted_emissions_to_avoided_emissions() method"""

    def test_convert_producted_emissions_to_avoided_emissions(self):
        """Test conversion from produced emissions rate to avoided emissions"""
        mock_biofuel = Mock()
        mock_biofuel.pci_litre = 35.5
        volume = 1000.0  # liters
        emissions_rate = 50.0  # gCO2/MJ

        result = TeneurService.convert_producted_emissions_to_avoided_emissions(volume, mock_biofuel, emissions_rate)

        # volume_energy = 1000 * 35.5 = 35500 MJ
        # avoided = (94 - 50) * 35500 / 1000000 = 1.562 tCO2
        expected = (94 - 50) * 35500 / 1000000
        self.assertEqual(result, expected)

    def test_convert_emissions_negative_for_high_emission_rate(self):
        """Test that avoided emissions can be negative if emissions exceed reference"""
        mock_biofuel = Mock()
        mock_biofuel.pci_litre = 35.5
        volume = 1000.0
        emissions_rate = 100.0  # Higher than reference (94)

        result = TeneurService.convert_producted_emissions_to_avoided_emissions(volume, mock_biofuel, emissions_rate)

        self.assertLess(result, 0)


class TeneurServicePrepareDataAndOptimizeTest(SimpleTestCase):
    """Test TeneurService.prepare_data_and_optimize() method"""

    @patch("tiruert.services.teneur.TeneurService.prepare_data")
    @patch("tiruert.services.teneur.TeneurService.optimize_biofuel_blending")
    def test_prepare_data_and_optimize_calls_prepare_data(self, mock_optimize, mock_prepare):
        """Test that prepare_data_and_optimize calls prepare_data with correct arguments"""
        mock_biofuel = Mock()
        mock_biofuel.pci_litre = 35.5
        data = {
            "biofuel": mock_biofuel,
            "target_volume": 1000.0,
            "target_emission": 1.5,
        }
        volumes = np.array([100.0, 200.0])
        emissions = np.array([50.0, 60.0])
        lot_ids = np.array([1, 2])
        enforced_volumes = None
        target_volume = 1000.0

        mock_prepare.return_value = (volumes, emissions, lot_ids, enforced_volumes, target_volume)
        mock_optimize.return_value = ({0: 100.0, 1: 900.0}, 0.5)

        selected_lots, returned_lot_ids, fun = TeneurService.prepare_data_and_optimize(data)

        mock_prepare.assert_called_once_with(data)
        self.assertIsNotNone(selected_lots)

    @patch("tiruert.services.teneur.TeneurService.prepare_data")
    @patch("tiruert.services.teneur.TeneurService.optimize_biofuel_blending")
    def test_prepare_data_and_optimize_calls_optimize_with_correct_params(self, mock_optimize, mock_prepare):
        """Test that optimize_biofuel_blending is called with correct parameters"""
        mock_biofuel = Mock()
        mock_biofuel.pci_litre = 35.5
        data = {
            "biofuel": mock_biofuel,
            "target_volume": 1000.0,
            "target_emission": 1.5,
        }
        volumes = np.array([100.0, 200.0])
        emissions = np.array([50.0, 60.0])
        lot_ids = np.array([1, 2])
        enforced_volumes = None
        target_volume = 1000.0

        mock_prepare.return_value = (volumes, emissions, lot_ids, enforced_volumes, target_volume)
        mock_optimize.return_value = ({0: 100.0, 1: 900.0}, 0.5)

        TeneurService.prepare_data_and_optimize(data)

        # Verify optimize was called with correct arguments
        mock_optimize.assert_called_once()
        call_args = mock_optimize.call_args[0]
        np.testing.assert_array_equal(call_args[0], volumes)
        np.testing.assert_array_equal(call_args[1], emissions)
        self.assertEqual(call_args[2], target_volume)

    @patch("tiruert.services.teneur.log_warning")
    def test_logs_negative_volumes(self, patched_log_warning):
        data = {"biofuel": "Biofuel infos", "customs_category": "Some category", "other_key": "Other value"}
        debited_entity = "Some entity"
        volumes = np.array([10, -20, 50, -30, 40])
        lot_ids = np.array([1, 2, 5, 3, 4])
        negative_volumes = np.array([-20, -30])
        patched_log_warning.assert_not_called()

        TeneurService.log_negative_volumes(data, debited_entity, volumes, lot_ids, negative_volumes)
        expected_logged_message = (
            "Negative volumes detected in balance calculation: "
            "2 lots with volumes ranging from -30.00L to -20.00L. "
            "Lot IDs: [2, 3]"
        )
        expected_additional_informations = {
            "biofuel": "Biofuel infos",
            "customs_category": "Some category",
            "debited_entity": "Some entity",
        }
        patched_log_warning.assert_called_with(expected_logged_message, expected_additional_informations)


class TeneurServicePrepareDataTest(SimpleTestCase):
    """Unit tests for TeneurService.prepare_data() new filter parameters."""

    def _make_data(self, **extra):
        mock_entity = Mock()
        mock_entity.id = 1
        mock_biofuel = Mock()
        mock_biofuel.pci_litre = 35.5
        return {
            "biofuel": mock_biofuel,
            "customs_category": "CONV",
            "debited_entity": mock_entity,
            **extra,
        }

    def _mock_operations_chain(self):
        mock_qs = Mock()
        mock_qs.filter.return_value = mock_qs
        mock_qs.distinct.return_value = mock_qs
        return mock_qs

    @patch("tiruert.services.teneur.BalanceService.calculate_balance")
    @patch("tiruert.services.teneur.Operation.objects")
    def test_prepare_data_passes_feedstock_to_detail_filters(self, mock_objects, mock_balance):
        """Test that feedstock is passed to BalanceService.calculate_balance detail_filters."""
        mock_qs = self._mock_operations_chain()
        mock_objects.filter.return_value = mock_qs
        mock_balance.return_value = {}

        data = self._make_data(feedstock=["COLZA", "TOURNESOL"])

        TeneurService.prepare_data(data)

        _, call_kwargs = mock_balance.call_args
        self.assertEqual(call_kwargs["detail_filters"]["feedstock"], ["COLZA", "TOURNESOL"])

    @patch("tiruert.services.teneur.BalanceService.calculate_balance")
    @patch("tiruert.services.teneur.Operation.objects")
    def test_prepare_data_passes_origin_country_to_detail_filters(self, mock_objects, mock_balance):
        """Test that origin_country is passed to BalanceService.calculate_balance detail_filters."""
        mock_qs = self._mock_operations_chain()
        mock_objects.filter.return_value = mock_qs
        mock_balance.return_value = {}

        data = self._make_data(origin_country=["FR", "DE"])

        TeneurService.prepare_data(data)

        _, call_kwargs = mock_balance.call_args
        self.assertEqual(call_kwargs["detail_filters"]["origin_country"], ["FR", "DE"])

    @patch("tiruert.services.teneur.BalanceService.calculate_balance")
    @patch("tiruert.services.teneur.Operation.objects")
    def test_prepare_data_passes_none_when_feedstock_not_provided(self, mock_objects, mock_balance):
        """Test that feedstock is None in detail_filters when not present in data."""
        mock_qs = self._mock_operations_chain()
        mock_objects.filter.return_value = mock_qs
        mock_balance.return_value = {}

        data = self._make_data()

        TeneurService.prepare_data(data)

        _, call_kwargs = mock_balance.call_args
        self.assertIsNone(call_kwargs["detail_filters"]["feedstock"])

    @patch("tiruert.services.teneur.BalanceService.calculate_balance")
    @patch("tiruert.services.teneur.Operation.objects")
    def test_prepare_data_passes_none_when_origin_country_not_provided(self, mock_objects, mock_balance):
        """Test that origin_country is None in detail_filters when not present in data."""
        mock_qs = self._mock_operations_chain()
        mock_objects.filter.return_value = mock_qs
        mock_balance.return_value = {}

        data = self._make_data()

        TeneurService.prepare_data(data)

        _, call_kwargs = mock_balance.call_args
        self.assertIsNone(call_kwargs["detail_filters"]["origin_country"])

    @patch("tiruert.services.teneur.BalanceService.resolve_lot_ids_for_durability_period")
    @patch("tiruert.services.teneur.BalanceService.calculate_balance")
    @patch("tiruert.services.teneur.Operation.objects")
    def test_prepare_data_passes_lot_ids_when_durability_period_provided(self, mock_objects, mock_balance, mock_resolve):
        """Test that when durability_period is provided, lot_ids is resolved via
        BalanceService.resolve_lot_ids_for_durability_period and passed to calculate_balance."""
        mock_qs = self._mock_operations_chain()
        mock_objects.filter.return_value = mock_qs
        mock_balance.return_value = {}
        mock_resolve.return_value = [10, 20, 30]

        data = self._make_data(durability_period=["2024", "2025"])

        TeneurService.prepare_data(data)

        mock_resolve.assert_called_once()
        _, call_kwargs = mock_balance.call_args
        self.assertEqual(call_kwargs["detail_filters"]["lot_ids"], [10, 20, 30])

    @patch("tiruert.services.teneur.BalanceService.calculate_balance")
    @patch("tiruert.services.teneur.Operation.objects")
    def test_prepare_data_no_lot_ids_when_durability_period_not_provided(self, mock_objects, mock_balance):
        """Test that lot_ids is None in detail_filters when no durability_period is provided."""
        mock_qs = self._mock_operations_chain()
        mock_objects.filter.return_value = mock_qs
        mock_balance.return_value = {}

        data = self._make_data()

        TeneurService.prepare_data(data)

        _, call_kwargs = mock_balance.call_args
        self.assertIsNone(call_kwargs["detail_filters"]["lot_ids"])


class TeneurServicePrepareDataDurabilityFilterTest(TestCase):
    """Integration test: verify that filtering by durability_period resolves to lot_ids
    from credit operations of that period, so the balance is computed on those specific lots
    (including all debit operations that consumed them)."""

    fixtures = [
        "json/biofuels.json",
        "json/feedstock.json",
        "json/countries.json",
        "json/depots.json",
        "json/entities.json",
        "json/entities_sites.json",
    ]

    def setUp(self):
        from core.models import Biocarburant, Entity
        from entity.factories.entity import EntityFactory
        from tiruert.factories.operation import OperationDetailFactory, OperationFactory

        self.entity = EntityFactory.create(entity_type=Entity.OPERATOR)
        self.biofuel = Biocarburant.objects.first()
        self.common = {
            "biofuel": self.biofuel,
            "customs_category": "CONV",
            "status": Operation.VALIDATED,
        }
        # Credit operation for period 2024 with a detail (lot)
        self.op_2024 = OperationFactory.create(
            credited_entity=self.entity,
            durability_period="2024",
            **self.common,
        )
        self.detail_2024 = OperationDetailFactory.create_for_operation(self.op_2024)

        # Credit operation for period 2025 with a different lot
        self.op_2025 = OperationFactory.create(
            credited_entity=self.entity,
            durability_period="2025",
            **self.common,
        )
        self.detail_2025 = OperationDetailFactory.create_for_operation(self.op_2025)

    @patch("tiruert.services.teneur.BalanceService.calculate_balance")
    def test_durability_period_resolves_to_lot_ids_of_that_period(self, mock_balance):
        """When filtering by durability_period=['2024'], the lot_ids passed to
        calculate_balance must only include lots from operations with durability_period='2024',
        not those from '2025'."""
        mock_balance.return_value = {}
        data = {
            "biofuel": self.biofuel,
            "customs_category": "CONV",
            "debited_entity": self.entity,
            "durability_period": ["2024"],
        }

        TeneurService.prepare_data(data)

        _, call_kwargs = mock_balance.call_args
        lot_ids = call_kwargs["detail_filters"]["lot_ids"]

        self.assertIn(self.detail_2024.lot_id, lot_ids, "Lot from period 2024 must be in lot_ids")
        self.assertNotIn(self.detail_2025.lot_id, lot_ids, "Lot from period 2025 must not be in lot_ids")

    @patch("tiruert.services.teneur.BalanceService.calculate_balance")
    def test_no_durability_period_passes_no_lot_ids_filter(self, mock_balance):
        """When no durability_period is provided, lot_ids in detail_filters must be None
        so all lots are considered."""
        mock_balance.return_value = {}
        data = {
            "biofuel": self.biofuel,
            "customs_category": "CONV",
            "debited_entity": self.entity,
        }

        TeneurService.prepare_data(data)

        _, call_kwargs = mock_balance.call_args
        self.assertIsNone(call_kwargs["detail_filters"]["lot_ids"])


class TeneurServiceGetMinAndMaxEmissionsTest(SimpleTestCase):
    """Test TeneurService.get_min_and_max_emissions() method"""

    @patch("tiruert.services.teneur.TeneurService.prepare_data")
    @patch("tiruert.services.teneur.TeneurService.emission_bounds")
    @patch("tiruert.services.teneur.TeneurService.convert_producted_emissions_to_avoided_emissions")
    def test_get_min_and_max_emissions_calls_prepare_data(self, mock_convert, mock_bounds, mock_prepare):
        """Test that get_min_and_max_emissions calls prepare_data"""
        mock_biofuel = Mock()
        mock_biofuel.pci_litre = 35.5
        data = {"biofuel": mock_biofuel, "target_volume": 1000.0}
        volumes = np.array([100.0, 200.0])
        emissions = np.array([50.0, 60.0])
        lot_ids = np.array([1, 2])
        enforced_volumes = None
        target_volume = 1000.0

        mock_prepare.return_value = (volumes, emissions, lot_ids, enforced_volumes, target_volume)
        mock_bounds.return_value = (50.0, 60.0)
        mock_convert.side_effect = [2.0, 1.5]  # max_avoided, min_avoided

        min_avoided, max_avoided = TeneurService.get_min_and_max_emissions(data)

        mock_prepare.assert_called_once_with(data)
        self.assertEqual(min_avoided, 1.5)
        self.assertEqual(max_avoided, 2.0)

    @patch("tiruert.services.teneur.TeneurService.prepare_data")
    @patch("tiruert.services.teneur.TeneurService.emission_bounds")
    @patch("tiruert.services.teneur.TeneurService.convert_producted_emissions_to_avoided_emissions")
    def test_get_min_and_max_emissions_returns_correct_order(self, mock_convert, mock_bounds, mock_prepare):
        """Test that get_min_and_max_emissions returns (min_avoided, max_avoided) in correct order"""
        mock_biofuel = Mock()
        data = {"biofuel": mock_biofuel, "target_volume": 1000.0}
        mock_prepare.return_value = (np.array([100.0]), np.array([50.0]), np.array([1]), None, 1000.0)
        mock_bounds.return_value = (40.0, 70.0)  # min_rate, max_rate
        mock_convert.side_effect = [3.0, 1.0]  # Conversions for min_rate (→max_avoided), max_rate (→min_avoided)

        min_avoided, max_avoided = TeneurService.get_min_and_max_emissions(data)

        # min_avoided should correspond to max emission rate
        # max_avoided should correspond to min emission rate
        self.assertEqual(min_avoided, 1.0)
        self.assertEqual(max_avoided, 3.0)
