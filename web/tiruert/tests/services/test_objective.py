from unittest.mock import Mock, patch

from django.test import TestCase

from tiruert.models.elec_operation import ElecOperation
from tiruert.services.objective import ObjectiveService
from tiruert.services.teneur import GHG_REFERENCE_RED_II


class ObjectiveServiceApplyGhgConversionTest(TestCase):
    """Unit tests for ObjectiveService.apply_ghg_conversion() method."""

    def test_apply_ghg_conversion_converts_mj_to_tco2(self):
        """Test apply_ghg_conversion converts MJ to tCO2 using GHG_REFERENCE_RED_II."""
        value_mj = 5000  # MJ
        expected = value_mj * GHG_REFERENCE_RED_II / 1_000_000

        result = ObjectiveService.apply_ghg_conversion(value_mj)
        self.assertEqual(result, expected)

    def test_apply_ghg_conversion_returns_zero_for_zero_input(self):
        """Test apply_ghg_conversion returns 0 for 0 input."""
        result = ObjectiveService.apply_ghg_conversion(0)
        self.assertEqual(result, 0)


class ObjectiveServiceApplyElecGhgConversionTest(TestCase):
    """Unit tests for ObjectiveService.apply_elec_ghg_conversion() method."""

    def test_apply_elec_ghg_conversion_converts_mj_to_tco2(self):
        """Test apply_elec_ghg_conversion converts MJ to tCO2 using ElecOperation.EMISSION_RATE_PER_MJ."""
        value_mj = 5000  # MJ
        expected = value_mj * ElecOperation.EMISSION_RATE_PER_MJ / 1_000_000

        result = ObjectiveService.apply_elec_ghg_conversion(value_mj)
        self.assertEqual(result, expected)

    def test_apply_elec_ghg_conversion_returns_zero_for_zero_input(self):
        """Test apply_elec_ghg_conversion returns 0 for 0 input."""
        result = ObjectiveService.apply_elec_ghg_conversion(0)
        self.assertEqual(result, 0)


class ObjectiveServiceCalculatePenaltyTest(TestCase):
    """Unit tests for ObjectiveService._calcule_penalty() method."""

    def test_calcule_penalty_returns_penalty_when_teneur_below_target(self):
        """Test _calcule_penalty calculates penalty when teneur is below target."""
        penalty_rate = 100  # c€/GJ
        teneur = 500_000  # MJ
        target = 1_000_000  # MJ

        result = ObjectiveService._calcule_penalty(penalty_rate, teneur, target, tCO2=False)

        # diff = (1_000_000 - 500_000) / 1000 = 500 GJ
        # penalty = 500 * 100 = 50_000
        self.assertEqual(result, 50_000)

    def test_calcule_penalty_returns_zero_when_teneur_equals_target(self):
        """Test _calcule_penalty returns 0 when teneur equals target."""
        penalty_rate = 100
        teneur = 1_000_000
        target = 1_000_000

        result = ObjectiveService._calcule_penalty(penalty_rate, teneur, target)
        self.assertEqual(result, 0)

    def test_calcule_penalty_returns_zero_when_teneur_exceeds_target(self):
        """Test _calcule_penalty returns 0 when teneur exceeds target."""
        penalty_rate = 100
        teneur = 1_500_000
        target = 1_000_000

        result = ObjectiveService._calcule_penalty(penalty_rate, teneur, target)
        self.assertEqual(result, 0)

    def test_calcule_penalty_returns_zero_when_penalty_is_none(self):
        """Test _calcule_penalty returns 0 when penalty rate is None."""
        result = ObjectiveService._calcule_penalty(None, 500_000, 1_000_000)
        self.assertEqual(result, 0)

    def test_calcule_penalty_returns_zero_when_target_is_none(self):
        """Test _calcule_penalty returns 0 when target is None."""
        result = ObjectiveService._calcule_penalty(100, 500_000, None)
        self.assertEqual(result, 0)

    def test_calcule_penalty_returns_zero_when_target_is_zero(self):
        """Test _calcule_penalty returns 0 when target is 0."""
        result = ObjectiveService._calcule_penalty(100, 500_000, 0)
        self.assertEqual(result, 0)

    def test_calcule_penalty_in_tco2_mode_does_not_divide_by_1000(self):
        """Test _calcule_penalty in tCO2 mode doesn't divide diff by 1000."""
        penalty_rate = 100  # c€/tCO2
        teneur = 50  # tCO2
        target = 100  # tCO2

        result = ObjectiveService._calcule_penalty(penalty_rate, teneur, target, tCO2=True)

        # diff = 100 - 50 = 50 tCO2 (no division by 1000)
        # penalty = 50 * 100 = 5_000
        self.assertEqual(result, 5_000)


class ObjectiveServiceCalculateTargetForObjectiveTest(TestCase):
    """Unit tests for ObjectiveService._calculate_target_for_objective() method."""

    def test_calculate_target_multiplies_target_by_energy_basis(self):
        """Test _calculate_target_for_objective multiplies target by energy_basis."""
        target = 0.1  # 10%
        energy_basis = 10_000_000  # MJ

        result = ObjectiveService._calculate_target_for_objective(target, energy_basis)
        self.assertEqual(result, 1_000_000)  # 10% of 10M = 1M

    def test_calculate_target_with_zero_target(self):
        """Test _calculate_target_for_objective returns 0 when target is 0."""
        result = ObjectiveService._calculate_target_for_objective(0, 10_000_000)
        self.assertEqual(result, 0)

    def test_calculate_target_with_zero_energy_basis(self):
        """Test _calculate_target_for_objective returns 0 when energy_basis is 0."""
        result = ObjectiveService._calculate_target_for_objective(0.1, 0)
        self.assertEqual(result, 0)


class ObjectiveServiceGetGlobalObjectiveAndPenaltyTest(TestCase):
    """Unit tests for ObjectiveService.get_global_objective_and_penalty() method."""

    def test_get_global_objective_returns_target_penalty_percent(self):
        """Test get_global_objective_and_penalty returns target, penalty, and target_percent."""
        mock_queryset = Mock()
        mock_queryset.filter.return_value.values.return_value.first.return_value = {
            "target": 0.1,
            "penalty": 100,
        }
        energy_basis = 10_000_000

        target, penalty, target_percent = ObjectiveService.get_global_objective_and_penalty(mock_queryset, energy_basis)

        self.assertEqual(target, 1_000_000)  # 10% of 10M
        self.assertEqual(penalty, 100)
        self.assertEqual(target_percent, 0.1)

    def test_get_global_objective_returns_zeros_when_no_objective(self):
        """Test get_global_objective_and_penalty returns zeros when no objective found."""
        mock_queryset = Mock()
        mock_queryset.filter.return_value.values.return_value.first.return_value = None

        target, penalty, target_percent = ObjectiveService.get_global_objective_and_penalty(mock_queryset, 10_000_000)

        self.assertEqual(target, 0)
        self.assertEqual(penalty, 0)
        self.assertEqual(target_percent, 0)


class ObjectiveServiceAggregateObjectivesTest(TestCase):
    """Unit tests for ObjectiveService.aggregate_objectives() method."""

    def test_aggregate_objectives_returns_none_for_empty_list(self):
        """Test aggregate_objectives returns None for empty list."""
        result = ObjectiveService.aggregate_objectives([])

        self.assertIsNone(result)

    def test_aggregate_objectives_returns_single_item_unchanged(self):
        """Test aggregate_objectives returns single item structure unchanged."""
        objectives = [
            {
                "main": {
                    "available_balance": 100,
                    "target": 200,
                    "pending_teneur": 50,
                    "declared_teneur": 30,
                    "penalty": 10,
                    "energy_basis": 1000,
                    "target_percent": 0.1,
                },
                "sectors": [
                    {
                        "code": "ESSENCE",
                        "available_balance": 100,
                        "pending_teneur": 50,
                        "declared_teneur": 30,
                        "objective": {"target_mj": 200, "penalty": 10},
                    }
                ],
                "categories": [
                    {
                        "code": "CONV",
                        "available_balance": 80,
                        "pending_teneur": 40,
                        "declared_teneur": 20,
                        "objective": {"target_mj": 150, "penalty": 5},
                    }
                ],
            }
        ]

        result = ObjectiveService.aggregate_objectives(objectives)

        self.assertEqual(result["main"]["available_balance"], 100)
        self.assertEqual(result["main"]["target_percent"], 0.1)
        self.assertEqual(len(result["sectors"]), 1)
        self.assertEqual(len(result["categories"]), 1)

    def test_aggregate_objectives_sums_main_values(self):
        """Test aggregate_objectives sums main values across multiple objectives."""
        objectives = [
            {
                "main": {
                    "available_balance": 100,
                    "target": 200,
                    "pending_teneur": 50,
                    "declared_teneur": 30,
                    "penalty": 10,
                    "energy_basis": 1000,
                    "target_percent": 0.1,
                },
                "sectors": [],
                "categories": [],
            },
            {
                "main": {
                    "available_balance": 150,
                    "target": 300,
                    "pending_teneur": 60,
                    "declared_teneur": 40,
                    "penalty": 15,
                    "energy_basis": 1500,
                    "target_percent": 0.1,
                },
                "sectors": [],
                "categories": [],
            },
        ]

        result = ObjectiveService.aggregate_objectives(objectives)

        self.assertEqual(result["main"]["available_balance"], 250)  # 100 + 150
        self.assertEqual(result["main"]["target"], 500)  # 200 + 300
        self.assertEqual(result["main"]["pending_teneur"], 110)  # 50 + 60
        self.assertEqual(result["main"]["declared_teneur"], 70)  # 30 + 40
        self.assertEqual(result["main"]["penalty"], 25)  # 10 + 15
        self.assertEqual(result["main"]["energy_basis"], 2500)  # 1000 + 1500

    def test_aggregate_objectives_takes_first_non_none_target_percent(self):
        """Test aggregate_objectives takes first non-None target_percent."""
        main_base = {
            "available_balance": 0,
            "target": 0,
            "pending_teneur": 0,
            "declared_teneur": 0,
            "penalty": 0,
            "energy_basis": 0,
        }
        objectives = [
            {"main": {**main_base, "target_percent": None}, "sectors": [], "categories": []},
            {"main": {**main_base, "target_percent": 0.15}, "sectors": [], "categories": []},
            {"main": {**main_base, "target_percent": 0.20}, "sectors": [], "categories": []},
        ]

        result = ObjectiveService.aggregate_objectives(objectives)

        self.assertEqual(result["main"]["target_percent"], 0.15)  # First non-None

    def test_aggregate_objectives_aggregates_sectors_by_code(self):
        """Test aggregate_objectives aggregates sectors with same code."""
        main_base = {
            "available_balance": 0,
            "target": 0,
            "pending_teneur": 0,
            "declared_teneur": 0,
            "penalty": 0,
            "energy_basis": 0,
            "target_percent": 0.1,
        }
        objectives = [
            {
                "main": main_base,
                "sectors": [
                    {
                        "code": "ESSENCE",
                        "available_balance": 100,
                        "pending_teneur": 50,
                        "declared_teneur": 30,
                        "objective": {"target_mj": 200, "penalty": 10},
                    },
                    {
                        "code": "GAZOLE",
                        "available_balance": 80,
                        "pending_teneur": 40,
                        "declared_teneur": 20,
                        "objective": {"target_mj": 150, "penalty": 5},
                    },
                ],
                "categories": [],
            },
            {
                "main": main_base,
                "sectors": [
                    {
                        "code": "ESSENCE",
                        "available_balance": 120,
                        "pending_teneur": 60,
                        "declared_teneur": 40,
                        "objective": {"target_mj": 250, "penalty": 12},
                    },
                ],
                "categories": [],
            },
        ]

        result = ObjectiveService.aggregate_objectives(objectives)

        self.assertEqual(len(result["sectors"]), 2)  # ESSENCE and GAZOLE

        # Find ESSENCE sector
        essence_sector = next((s for s in result["sectors"] if s["code"] == "ESSENCE"), None)
        self.assertIsNotNone(essence_sector)
        self.assertEqual(essence_sector["available_balance"], 220)  # 100 + 120
        self.assertEqual(essence_sector["pending_teneur"], 110)  # 50 + 60
        self.assertEqual(essence_sector["declared_teneur"], 70)  # 30 + 40
        self.assertEqual(essence_sector["objective"]["target_mj"], 450)  # 200 + 250
        self.assertEqual(essence_sector["objective"]["penalty"], 22)  # 10 + 12

        # GAZOLE should be unchanged (only one entry)
        gazole_sector = next((s for s in result["sectors"] if s["code"] == "GAZOLE"), None)
        self.assertIsNotNone(gazole_sector)
        self.assertEqual(gazole_sector["available_balance"], 80)

    def test_aggregate_objectives_aggregates_categories_by_code(self):
        """Test aggregate_objectives aggregates categories with same code."""
        main_base = {
            "available_balance": 0,
            "target": 0,
            "pending_teneur": 0,
            "declared_teneur": 0,
            "penalty": 0,
            "energy_basis": 0,
            "target_percent": 0.1,
        }
        objectives = [
            {
                "main": main_base,
                "sectors": [],
                "categories": [
                    {
                        "code": "CONV",
                        "available_balance": 100,
                        "pending_teneur": 50,
                        "declared_teneur": 30,
                        "objective": {"target_mj": 200, "penalty": 10},
                    },
                ],
            },
            {
                "main": main_base,
                "sectors": [],
                "categories": [
                    {
                        "code": "CONV",
                        "available_balance": 150,
                        "pending_teneur": 70,
                        "declared_teneur": 50,
                        "objective": {"target_mj": 300, "penalty": 15},
                    },
                    {
                        "code": "ANN2",
                        "available_balance": 50,
                        "pending_teneur": 20,
                        "declared_teneur": 10,
                        "objective": {"target_mj": 100, "penalty": 5},
                    },
                ],
            },
        ]

        result = ObjectiveService.aggregate_objectives(objectives)

        self.assertEqual(len(result["categories"]), 2)  # CONV and ANN2

        # Find CONV category
        conv_category = next((c for c in result["categories"] if c["code"] == "CONV"), None)
        self.assertIsNotNone(conv_category)
        self.assertEqual(conv_category["available_balance"], 250)  # 100 + 150
        self.assertEqual(conv_category["objective"]["target_mj"], 500)  # 200 + 300

    def test_aggregate_objectives_handles_none_objective_values(self):
        """Test aggregate_objectives handles None values in objective dict."""
        main_base = {
            "available_balance": 100,
            "target": 200,
            "pending_teneur": 50,
            "declared_teneur": 30,
            "penalty": 10,
            "energy_basis": 1000,
            "target_percent": 0.1,
        }
        objectives = [
            {
                "main": main_base,
                "sectors": [
                    {
                        "code": "ESSENCE",
                        "available_balance": 100,
                        "pending_teneur": 50,
                        "declared_teneur": 30,
                        "objective": {"target_mj": None, "penalty": None},
                    },
                ],
                "categories": [],
            },
            {
                "main": main_base,
                "sectors": [
                    {
                        "code": "ESSENCE",
                        "available_balance": 120,
                        "pending_teneur": 60,
                        "declared_teneur": 40,
                        "objective": {"target_mj": 200, "penalty": 10},
                    },
                ],
                "categories": [],
            },
        ]

        result = ObjectiveService.aggregate_objectives(objectives)

        essence_sector = next((s for s in result["sectors"] if s["code"] == "ESSENCE"), None)
        self.assertEqual(essence_sector["objective"]["target_mj"], 200)  # Only the non-None value
        self.assertEqual(essence_sector["objective"]["penalty"], 10)

    def test_aggregate_objectives_does_not_mutate_input(self):
        """Test aggregate_objectives does not mutate the input list."""
        original_value = 100
        main_data = {
            "available_balance": original_value,
            "target": 0,
            "pending_teneur": 0,
            "declared_teneur": 0,
            "penalty": 0,
            "energy_basis": 0,
            "target_percent": 0.1,
        }
        sector_data = {
            "code": "ESSENCE",
            "available_balance": original_value,
            "pending_teneur": 0,
            "declared_teneur": 0,
            "objective": {"target_mj": original_value, "penalty": 0},
        }
        objectives = [
            {
                "main": main_data,
                "sectors": [sector_data],
                "categories": [],
            },
        ]

        ObjectiveService.aggregate_objectives(objectives)

        # Original should not be mutated
        self.assertEqual(objectives[0]["main"]["available_balance"], original_value)
        self.assertEqual(objectives[0]["sectors"][0]["available_balance"], original_value)


class ObjectiveServiceAggregateItemsTest(TestCase):
    """Unit tests for ObjectiveService._aggregate_items() method."""

    def test_aggregate_items_adds_new_item_to_empty_dict(self):
        """Test _aggregate_items adds new item when aggregated dict is empty."""
        items = [{"code": "ESSENCE", "available_balance": 100, "pending_teneur": 50, "declared_teneur": 30}]
        aggregated = {}
        balance_keys = ["available_balance", "pending_teneur", "declared_teneur"]
        objective_keys = []

        ObjectiveService._aggregate_items(items, aggregated, balance_keys, objective_keys)

        self.assertIn("ESSENCE", aggregated)
        self.assertEqual(aggregated["ESSENCE"]["available_balance"], 100)

    def test_aggregate_items_sums_balance_keys_for_existing_code(self):
        """Test _aggregate_items sums balance keys when code already exists."""
        aggregated = {"ESSENCE": {"code": "ESSENCE", "available_balance": 100, "pending_teneur": 50, "declared_teneur": 30}}
        items = [{"code": "ESSENCE", "available_balance": 50, "pending_teneur": 25, "declared_teneur": 15}]
        balance_keys = ["available_balance", "pending_teneur", "declared_teneur"]
        objective_keys = []

        ObjectiveService._aggregate_items(items, aggregated, balance_keys, objective_keys)

        self.assertEqual(aggregated["ESSENCE"]["available_balance"], 150)  # 100 + 50
        self.assertEqual(aggregated["ESSENCE"]["pending_teneur"], 75)  # 50 + 25
        self.assertEqual(aggregated["ESSENCE"]["declared_teneur"], 45)  # 30 + 15

    def test_aggregate_items_sums_objective_keys(self):
        """Test _aggregate_items sums objective keys when present."""
        aggregated = {
            "ESSENCE": {
                "code": "ESSENCE",
                "available_balance": 100,
                "objective": {"target_mj": 200, "penalty": 10},
            }
        }
        items = [
            {
                "code": "ESSENCE",
                "available_balance": 50,
                "objective": {"target_mj": 100, "penalty": 5},
            }
        ]
        balance_keys = ["available_balance"]
        objective_keys = ["target_mj", "penalty"]

        ObjectiveService._aggregate_items(items, aggregated, balance_keys, objective_keys)

        self.assertEqual(aggregated["ESSENCE"]["objective"]["target_mj"], 300)  # 200 + 100
        self.assertEqual(aggregated["ESSENCE"]["objective"]["penalty"], 15)  # 10 + 5

    def test_aggregate_items_initializes_none_objective_key_to_zero(self):
        """Test _aggregate_items initializes None objective key to 0 before adding."""
        aggregated = {
            "ESSENCE": {
                "code": "ESSENCE",
                "available_balance": 100,
                "objective": {"target_mj": None, "penalty": None},
            }
        }
        items = [
            {
                "code": "ESSENCE",
                "available_balance": 50,
                "objective": {"target_mj": 100, "penalty": 5},
            }
        ]
        balance_keys = ["available_balance"]
        objective_keys = ["target_mj", "penalty"]

        ObjectiveService._aggregate_items(items, aggregated, balance_keys, objective_keys)

        self.assertEqual(aggregated["ESSENCE"]["objective"]["target_mj"], 100)  # 0 + 100
        self.assertEqual(aggregated["ESSENCE"]["objective"]["penalty"], 5)  # 0 + 5


class ObjectiveServiceCalculateGlobalObjectiveTest(TestCase):
    """Unit tests for ObjectiveService.calculate_global_objective() method."""

    @patch.object(ObjectiveService, "get_global_objective_and_penalty")
    @patch.object(ObjectiveService, "_calcule_penalty")
    def test_calculate_global_objective_sums_sector_values(self, mock_penalty, mock_global):
        """Test calculate_global_objective sums available_balance, pending_teneur, declared_teneur from all sectors."""
        mock_global.return_value = (1_000_000, 100, 0.1)
        mock_penalty.return_value = 0

        objective_per_sector = [
            {"available_balance": 100_000, "pending_teneur": 50_000, "declared_teneur": 30_000},
            {"available_balance": 150_000, "pending_teneur": 60_000, "declared_teneur": 40_000},
        ]
        elec_category = {"available_balance": 0, "pending_teneur": 0, "declared_teneur": 0}

        result = ObjectiveService.calculate_global_objective(objective_per_sector, elec_category, Mock(), 10_000_000)

        # Verify sectors are summed: 100_000 + 150_000 = 250_000, then GHG converted
        expected_available = ObjectiveService.apply_ghg_conversion(250_000)
        expected_pending = ObjectiveService.apply_ghg_conversion(110_000)  # 50_000 + 60_000
        expected_declared = ObjectiveService.apply_ghg_conversion(70_000)  # 30_000 + 40_000

        self.assertEqual(result["available_balance"], expected_available)
        self.assertEqual(result["pending_teneur"], expected_pending)
        self.assertEqual(result["declared_teneur"], expected_declared)

    @patch.object(ObjectiveService, "get_global_objective_and_penalty")
    @patch.object(ObjectiveService, "_calcule_penalty")
    def test_calculate_global_objective_combines_biofuel_and_elec(self, mock_penalty, mock_global):
        """Test calculate_global_objective combines biofuel and elec contributions."""
        mock_global.return_value = (0, 0, 0)
        mock_penalty.return_value = 0

        objective_per_sector = [{"available_balance": 1_000_000, "pending_teneur": 500_000, "declared_teneur": 200_000}]
        elec_category = {"available_balance": 100_000, "pending_teneur": 50_000, "declared_teneur": 20_000}

        result = ObjectiveService.calculate_global_objective(objective_per_sector, elec_category, Mock(), 10_000_000)

        # Result should include both biofuel (with GHG conversion) and elec (with elec conversion)
        biofuel_balance = ObjectiveService.apply_ghg_conversion(1_000_000)
        elec_balance = ObjectiveService.apply_elec_ghg_conversion(100_000)
        self.assertEqual(result["available_balance"], biofuel_balance + elec_balance)


class ObjectiveServiceGetElecCategoryTest(TestCase):
    """Unit tests for ObjectiveService.get_elec_category() method."""

    @patch("tiruert.services.objective.ElecBalanceService.calculate_balance")
    def test_get_elec_category_returns_formatted_category(self, mock_balance):
        """Test get_elec_category returns properly formatted elec category."""
        mock_balance.return_value = {
            "available_balance": 100,
            "pending_teneur": 50,
            "declared_teneur": 30,
        }

        result = ObjectiveService.get_elec_category(Mock(), 1, "2025-01-01")

        self.assertEqual(result["code"], ElecOperation.SECTOR)
        self.assertEqual(result["unit"], "mj")
        self.assertIn("objective", result)
        self.assertIsNone(result["objective"]["target_mj"])
        self.assertIsNone(result["objective"]["penalty"])


class ObjectiveServiceGetBalancesForObjectivesCalculationTest(TestCase):
    """Unit tests for ObjectiveService.get_balances_for_objectives_calculation() method."""

    @patch("tiruert.services.objective.BalanceService.calculate_balance")
    def test_get_balances_returns_category_and_sector_balances(self, mock_balance):
        """Test get_balances_for_objectives_calculation returns both balances."""
        mock_balance.side_effect = [{"category": "data"}, {"sector": "data"}]

        result = ObjectiveService.get_balances_for_objectives_calculation(Mock(), 1, "2025-01-01")

        self.assertEqual(len(result), 2)
        self.assertEqual(mock_balance.call_count, 2)

    @patch("tiruert.services.objective.BalanceService.calculate_balance")
    def test_get_balances_calls_balance_service_with_correct_params(self, mock_balance):
        """Test get_balances_for_objectives_calculation calls BalanceService correctly."""
        mock_balance.return_value = {}
        mock_operations = Mock()
        entity_id = 42

        ObjectiveService.get_balances_for_objectives_calculation(mock_operations, entity_id, "2025-06-15")

        # Should be called twice: once for category, once for sector
        self.assertEqual(mock_balance.call_count, 2)

        # First call for category
        first_call = mock_balance.call_args_list[0]
        self.assertEqual(first_call[0][0], mock_operations)
        self.assertEqual(first_call[0][1], entity_id)
        self.assertEqual(first_call[0][2], "customs_category")
        self.assertEqual(first_call[0][3], "mj")

        # Second call for sector
        second_call = mock_balance.call_args_list[1]
        self.assertEqual(second_call[0][2], "sector")
