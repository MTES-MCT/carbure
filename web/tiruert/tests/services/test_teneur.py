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

    def test_emission_bounds_insufficient_volume_raises_error(self):
        """Test that insufficient volume raises ValueError"""
        batches_volumes = np.array([100.0, 50.0])
        batches_emissions = np.array([50.0, 60.0])
        target_volume = 200.0  # More than available

        with self.assertRaises(ValueError) as context:
            TeneurService.emission_bounds(batches_volumes, batches_emissions, target_volume)

        self.assertEqual(str(context.exception), TeneurServiceErrors.INSUFFICIENT_INPUT_VOLUME)


class TeneurServiceConvertInLitersTest(SimpleTestCase):
    """Test TeneurService._convert_in_liters() method"""

    def test_convert_in_liters_returns_same_for_liter_unit(self):
        """Test that conversion returns same value for liter unit"""
        mock_biofuel = Mock()
        quantity = 100.0

        result = TeneurService._convert_in_liters(quantity, "l", mock_biofuel)

        self.assertEqual(result, 100.0)

    def test_convert_in_liters_converts_from_mj(self):
        """Test conversion from MJ to liters using pci_litre"""
        mock_biofuel = Mock()
        mock_biofuel.pci_litre = 35.5
        quantity = 355.0  # MJ

        result = TeneurService._convert_in_liters(quantity, "mj", mock_biofuel)

        self.assertEqual(result, 10.0)  # 355 / 35.5 = 10

    def test_convert_in_liters_converts_from_kg(self):
        """Test conversion from kg to liters using masse_volumique"""
        mock_biofuel = Mock()
        mock_biofuel.masse_volumique = 0.85
        quantity = 85.0  # kg

        result = TeneurService._convert_in_liters(quantity, "kg", mock_biofuel)

        self.assertEqual(result, 100.0)  # 85 / 0.85 = 100


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
        unit = "l"

        volumes = np.array([100.0, 200.0])
        emissions = np.array([50.0, 60.0])
        lot_ids = np.array([1, 2])
        enforced_volumes = None
        target_volume = 1000.0

        mock_prepare.return_value = (volumes, emissions, lot_ids, enforced_volumes, target_volume)
        mock_optimize.return_value = ({0: 100.0, 1: 900.0}, 0.5)

        selected_lots, returned_lot_ids, fun = TeneurService.prepare_data_and_optimize(data, unit)

        mock_prepare.assert_called_once_with(data, unit)
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
        unit = "l"

        volumes = np.array([100.0, 200.0])
        emissions = np.array([50.0, 60.0])
        lot_ids = np.array([1, 2])
        enforced_volumes = None
        target_volume = 1000.0

        mock_prepare.return_value = (volumes, emissions, lot_ids, enforced_volumes, target_volume)
        mock_optimize.return_value = ({0: 100.0, 1: 900.0}, 0.5)

        TeneurService.prepare_data_and_optimize(data, unit)

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

        TeneurService.prepare_data(data, "l")

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

        TeneurService.prepare_data(data, "l")

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

        TeneurService.prepare_data(data, "l")

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

        TeneurService.prepare_data(data, "l")

        _, call_kwargs = mock_balance.call_args
        self.assertIsNone(call_kwargs["detail_filters"]["origin_country"])

    @patch("tiruert.services.teneur.BalanceService.calculate_balance")
    @patch("tiruert.services.teneur.Operation.objects")
    def test_prepare_data_filters_operations_by_durability_period(self, mock_objects, mock_balance):
        """Test that durability_period causes an extra queryset filter."""
        mock_qs = self._mock_operations_chain()
        mock_objects.filter.return_value = mock_qs
        mock_balance.return_value = {}

        data = self._make_data(durability_period=["2024", "2025"])

        TeneurService.prepare_data(data, "l")

        # Verify that filter was called with durability_period__in
        filter_calls = [str(call) for call in mock_qs.filter.call_args_list]
        self.assertTrue(
            any("durability_period__in" in c for c in filter_calls),
            "Expected a filter call with durability_period__in",
        )

    @patch("tiruert.services.teneur.BalanceService.calculate_balance")
    @patch("tiruert.services.teneur.Operation.objects")
    def test_prepare_data_no_durability_period_filter_when_not_provided(self, mock_objects, mock_balance):
        """Test that no durability_period filter is applied when not in data."""
        mock_qs = self._mock_operations_chain()
        mock_objects.filter.return_value = mock_qs
        mock_balance.return_value = {}

        data = self._make_data()

        TeneurService.prepare_data(data, "l")

        filter_calls = [str(call) for call in mock_qs.filter.call_args_list]
        self.assertFalse(
            any("durability_period__in" in c for c in filter_calls),
            "Expected no filter call with durability_period__in",
        )


class TeneurServicePrepareDataDurabilityFilterTest(TestCase):
    """Integration test: verify that filtering by durability_period does not exclude
    debit operations (durability_period=None) from the balance calculation."""

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
        from tiruert.factories.operation import OperationFactory

        self.entity = EntityFactory.create(entity_type=Entity.OPERATOR)
        self.biofuel = Biocarburant.objects.first()
        self.common = {
            "biofuel": self.biofuel,
            "customs_category": "CONV",
            "status": Operation.VALIDATED,
        }
        # Credit operation with matching durability_period → must be included
        self.op_with_period = OperationFactory.create(
            credited_entity=self.entity,
            durability_period="2024",
            **self.common,
        )
        # Debit operation without durability_period (e.g. TENEUR) → must be included
        self.op_without_period = OperationFactory.create(
            debited_entity=self.entity,
            durability_period=None,
            **self.common,
        )
        # Credit operation with a different durability_period → must be excluded
        self.op_other_period = OperationFactory.create(
            credited_entity=self.entity,
            durability_period="2025",
            **self.common,
        )

    @patch("tiruert.services.teneur.BalanceService.calculate_balance")
    def test_durability_period_filter_includes_matching_and_null_operations(self, mock_balance):
        """When filtering by durability_period=['2024']:
        - the credit operation with durability_period='2024' is included,
        - the debit operation with durability_period=None is included (avoids inflated balance),
        - the credit operation with durability_period='2025' is excluded.
        """
        mock_balance.return_value = {}
        data = {
            "biofuel": self.biofuel,
            "customs_category": "CONV",
            "debited_entity": self.entity,
            "durability_period": ["2024"],
        }

        TeneurService.prepare_data(data, "l")

        # First positional arg of calculate_balance is the filtered operations queryset
        operations_qs = mock_balance.call_args[0][0]
        operation_ids = set(operations_qs.values_list("id", flat=True))

        self.assertIn(self.op_with_period.id, operation_ids, "Operation with durability_period='2024' must be included")
        self.assertIn(self.op_without_period.id, operation_ids, "Operation with durability_period=None must be included")
        self.assertNotIn(self.op_other_period.id, operation_ids, "Operation with durability_period='2025' must be excluded")


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
        unit = "l"

        volumes = np.array([100.0, 200.0])
        emissions = np.array([50.0, 60.0])
        lot_ids = np.array([1, 2])
        enforced_volumes = None
        target_volume = 1000.0

        mock_prepare.return_value = (volumes, emissions, lot_ids, enforced_volumes, target_volume)
        mock_bounds.return_value = (50.0, 60.0)
        mock_convert.side_effect = [2.0, 1.5]  # max_avoided, min_avoided

        min_avoided, max_avoided = TeneurService.get_min_and_max_emissions(data, unit)

        mock_prepare.assert_called_once_with(data, unit)
        self.assertEqual(min_avoided, 1.5)
        self.assertEqual(max_avoided, 2.0)

    @patch("tiruert.services.teneur.TeneurService.prepare_data")
    @patch("tiruert.services.teneur.TeneurService.emission_bounds")
    @patch("tiruert.services.teneur.TeneurService.convert_producted_emissions_to_avoided_emissions")
    def test_get_min_and_max_emissions_returns_correct_order(self, mock_convert, mock_bounds, mock_prepare):
        """Test that get_min_and_max_emissions returns (min_avoided, max_avoided) in correct order"""
        mock_biofuel = Mock()
        data = {"biofuel": mock_biofuel, "target_volume": 1000.0}
        unit = "l"

        mock_prepare.return_value = (np.array([100.0]), np.array([50.0]), np.array([1]), None, 1000.0)
        mock_bounds.return_value = (40.0, 70.0)  # min_rate, max_rate
        mock_convert.side_effect = [3.0, 1.0]  # Conversions for min_rate (→max_avoided), max_rate (→min_avoided)

        min_avoided, max_avoided = TeneurService.get_min_and_max_emissions(data, unit)

        # min_avoided should correspond to max emission rate
        # max_avoided should correspond to min emission rate
        self.assertEqual(min_avoided, 1.0)
        self.assertEqual(max_avoided, 3.0)
