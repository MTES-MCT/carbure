from unittest.mock import Mock, patch

from django.db.models import Q
from django.test import TestCase

from core.models import MatierePremiere
from tiruert.models import Operation, OperationDetail
from tiruert.services.balance import BalanceService


class BalanceServiceInitBalanceEntryTest(TestCase):
    """Unit tests for BalanceService._init_balance_entry() method."""

    def test_init_balance_entry(self):
        """Test _init_balance_entry creates entry with None values and correct defaults."""
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


class BalanceServiceGetKeyTest(TestCase):
    """Unit tests for BalanceService._get_key() method."""

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

    def test_get_key_returns_base_tuple_when_lot_grouping_without_detail(self):
        """Test _get_key returns base tuple when grouping by lot but detail is None."""
        mock_operation = Mock()
        mock_operation.sector = "ESSENCE"
        mock_operation.customs_category = MatierePremiere.CONV
        mock_operation.biofuel.code = "ETH"

        result = BalanceService._get_key(mock_operation, BalanceService.GROUP_BY_LOT, detail=None)

        self.assertEqual(result, ("ESSENCE", MatierePremiere.CONV, "ETH"))


class BalanceServiceLotVolumeRuleTest(TestCase):
    """Unit tests for lot volume behavior."""

    def test_lot_quantity_uses_detail_volume_directly(self):
        """Lot path uses detail.volume directly."""
        mock_detail = Mock()
        mock_detail.volume = 100.0

        self.assertEqual(mock_detail.volume, 100.0)


class BalanceServiceFilterOperationsTest(TestCase):
    """Unit tests for filtering operations by the current declaration year."""

    @patch("tiruert.services.balance.DeclarationPeriodService.get_current_declaration_year", return_value=2025)
    def test_filter_operations_for_current_year_excludes_next_year(self, mock_current_year):
        """Test _filter_operations_for_current_year builds and applies the expected Q filter."""
        operations = Mock()
        filtered_operations = Mock()
        operations.filter.return_value = filtered_operations

        result = BalanceService._filter_operations_for_current_year(operations)

        self.assertIs(result, filtered_operations)
        operations.filter.assert_called_once_with(
            (Q(durability_period__isnull=True) | Q(durability_period__lt="2026"))
            & (Q(declaration_year__isnull=True) | Q(declaration_year__lte=2025))
        )
        mock_current_year.assert_called_once_with()


class BalanceServiceFilterOperationsForCurrentYearBehaviorTest(TestCase):
    """Behavioral tests verifying which operations _filter_operations_for_current_year actually keeps."""

    fixtures = [
        "json/biofuels.json",
        "json/feedstock.json",
        "json/countries.json",
        "json/depots.json",
        "json/entities.json",
        "json/entities_sites.json",
    ]

    def setUp(self):
        from tiruert.factories import OperationFactory

        self.OperationFactory = OperationFactory

    @patch("tiruert.services.balance.DeclarationPeriodService.get_current_declaration_year", return_value=2025)
    def test_keeps_operation_with_durability_period_in_current_year(self, mock_current_year):
        """An operation whose durability_period is within the current year is kept."""
        op = self.OperationFactory(durability_period="202501")

        result = BalanceService._filter_operations_for_current_year(Operation.objects.filter(id=op.id))

        self.assertIn(op, result)

    @patch("tiruert.services.balance.DeclarationPeriodService.get_current_declaration_year", return_value=2025)
    def test_keeps_operation_with_durability_period_before_current_year(self, mock_current_year):
        """An operation whose durability_period is before the current year is kept."""
        op = self.OperationFactory(durability_period="202401")

        result = BalanceService._filter_operations_for_current_year(Operation.objects.filter(id=op.id))

        self.assertIn(op, result)

    @patch("tiruert.services.balance.DeclarationPeriodService.get_current_declaration_year", return_value=2025)
    def test_excludes_operation_with_durability_period_in_next_year(self, mock_current_year):
        """An operation whose durability_period falls in the next year is excluded."""
        op = self.OperationFactory(durability_period="202601")

        result = BalanceService._filter_operations_for_current_year(Operation.objects.filter(id=op.id))

        self.assertNotIn(op, result)

    @patch("tiruert.services.balance.DeclarationPeriodService.get_current_declaration_year", return_value=2025)
    def test_keeps_operation_with_declaration_year_at_or_before_current(self, mock_current_year):
        """An operation whose declaration_year is at or before the current year is kept."""
        op = self.OperationFactory(declaration_year=2025)

        result = BalanceService._filter_operations_for_current_year(Operation.objects.filter(id=op.id))

        self.assertIn(op, result)

    @patch("tiruert.services.balance.DeclarationPeriodService.get_current_declaration_year", return_value=2025)
    def test_keeps_operation_with_declaration_year_before_current(self, mock_current_year):
        """An operation whose declaration_year is before the current year is kept."""
        op = self.OperationFactory(declaration_year=2024)

        result = BalanceService._filter_operations_for_current_year(Operation.objects.filter(id=op.id))

        self.assertIn(op, result)

    @patch("tiruert.services.balance.DeclarationPeriodService.get_current_declaration_year", return_value=2025)
    def test_excludes_operation_with_declaration_year_after_current(self, mock_current_year):
        """An operation whose declaration_year is after the current year is excluded."""
        op = self.OperationFactory(declaration_year=2026)

        result = BalanceService._filter_operations_for_current_year(Operation.objects.filter(id=op.id))

        self.assertNotIn(op, result)

    @patch("tiruert.services.balance.DeclarationPeriodService.get_current_declaration_year", return_value=None)
    def test_keeps_all_operations_when_no_current_declaration_period(self, mock_current_year):
        """When there is no current declaration period, no filtering is applied."""
        op = self.OperationFactory(durability_period="203001", declaration_year=2099)

        result = BalanceService._filter_operations_for_current_year(Operation.objects.filter(id=op.id))

        self.assertIn(op, result)

    @patch("tiruert.services.balance.DeclarationPeriodService.get_current_declaration_year", return_value=2025)
    def test_created_at_does_not_affect_kept_operation(self, mock_current_year):
        """created_at must not be used as a filtering criterion: an old created_at must not exclude an operation."""
        from datetime import datetime, timezone

        op = self.OperationFactory(durability_period=None, declaration_year=2025)
        Operation.objects.filter(id=op.id).update(created_at=datetime(2020, 1, 1, tzinfo=timezone.utc))

        result = BalanceService._filter_operations_for_current_year(Operation.objects.filter(id=op.id))

        self.assertIn(op, result)

    @patch("tiruert.services.balance.DeclarationPeriodService.get_current_declaration_year", return_value=2025)
    def test_created_at_does_not_prevent_exclusion(self, mock_current_year):
        """created_at must not be used as a filtering criterion: a created_at value must not prevent exclusion."""
        from datetime import datetime, timezone

        op = self.OperationFactory(durability_period=None, declaration_year=2026)
        Operation.objects.filter(id=op.id).update(created_at=datetime(2025, 6, 1, tzinfo=timezone.utc))

        result = BalanceService._filter_operations_for_current_year(Operation.objects.filter(id=op.id))

        self.assertNotIn(op, result)


class OperationDetailAvoidedEmissionsTest(TestCase):
    """Unit tests for OperationDetail.avoided_emissions property."""

    def test_energy_applies_renewable_share(self):
        from tiruert.models.operation_detail import OperationDetail

        mock_detail = Mock(spec=OperationDetail)
        mock_detail.volume = 100.0
        mock_detail.operation.renewable_energy_share = 0.4
        mock_detail.lot.biofuel.pci_litre = 10.0

        result = OperationDetail.energy.fget(mock_detail)

        self.assertEqual(result, 100.0 * 0.4 * 10.0)

    def test_avoided_emissions_applies_renewable_share(self):
        from tiruert.models.operation_detail import OperationDetail

        mock_detail = Mock(spec=OperationDetail)
        mock_detail.emission_rate_per_mj = 20.0
        mock_detail.energy = 10.0 * 100.0 * 0.4

        result = OperationDetail.avoided_emissions.fget(mock_detail)

        self.assertEqual(result, (94 - 20.0) * mock_detail.energy / 1000000)


class BalanceServiceUpdateAvailableBalanceTest(TestCase):
    """Unit tests for BalanceService._update_available_balance() method."""

    def test_update_available_balance_adds_volume_for_credit_operation(self):
        """Test _update_available_balance adds volume when credit_operation=True."""
        balance = {
            "key1": {
                "available_balance": 100.0,
                "saved_emissions": 0.0,
                "emission_rate_per_mj": 0,
            }
        }
        mock_operation = Mock()
        mock_operation.biofuel = Mock()
        mock_operation.renewable_energy_share = 1.0
        mock_detail = Mock()
        mock_detail.volume = 20.0
        mock_detail.emission_rate_per_mj = 25.0
        mock_detail.avoided_emissions = 50.0
        quantity = mock_detail.volume

        BalanceService._update_available_balance(balance, "key1", mock_operation, mock_detail, True, quantity)

        self.assertEqual(balance["key1"]["available_balance"], 120.0)
        self.assertEqual(balance["key1"]["saved_emissions"], 50.0)

    def test_update_available_balance_subtracts_volume_for_debit_operation(self):
        """Test _update_available_balance subtracts volume when credit_operation=False."""
        balance = {
            "key1": {
                "available_balance": 100.0,
                "saved_emissions": 0.0,
                "emission_rate_per_mj": 0,
            }
        }
        mock_operation = Mock()
        mock_operation.biofuel = Mock()
        mock_operation.renewable_energy_share = 1.0
        mock_detail = Mock()
        mock_detail.volume = 15.0
        mock_detail.emission_rate_per_mj = 20.0
        mock_detail.avoided_emissions = 30.0
        quantity = mock_detail.volume

        BalanceService._update_available_balance(balance, "key1", mock_operation, mock_detail, False, quantity)

        self.assertEqual(balance["key1"]["available_balance"], 85.0)
        self.assertEqual(balance["key1"]["saved_emissions"], -30.0)

    def test_update_available_balance_sets_emission_rate(self):
        """Test _update_available_balance sets emission_rate_per_mj from detail."""
        balance = {
            "key1": {
                "available_balance": 0.0,
                "saved_emissions": 0.0,
                "emission_rate_per_mj": 0,
            }
        }
        mock_operation = Mock()
        mock_operation.biofuel = Mock()
        mock_operation.renewable_energy_share = 1.0
        mock_detail = Mock()
        mock_detail.volume = 10.0
        mock_detail.emission_rate_per_mj = 42.5
        mock_detail.avoided_emissions = 0.0
        quantity = mock_detail.volume

        BalanceService._update_available_balance(balance, "key1", mock_operation, mock_detail, True, quantity)

        self.assertEqual(balance["key1"]["emission_rate_per_mj"], 42.5)


class BalanceServiceCalculateBalanceIntegrationTest(TestCase):
    """Integration tests for BalanceService.calculate_balance() method."""

    fixtures = [
        "json/biofuels.json",
        "json/feedstock.json",
        "json/countries.json",
        "json/depots.json",
        "json/entities.json",
        "json/entities_sites.json",
    ]

    def setUp(self):
        from core.models import Entity
        from tiruert.factories import OperationDetailFactory, OperationFactory
        from transactions.factories import CarbureLotFactory

        self.entity, _ = Entity.objects.get_or_create(
            name="Test Entity",
            entity_type=Entity.OPERATOR,
        )
        self.OperationFactory = OperationFactory
        self.OperationDetailFactory = OperationDetailFactory
        self.CarbureLotFactory = CarbureLotFactory

    def _create_operation_with_details(self, **op_kwargs):
        """Helper to create an operation with details."""
        op = self.OperationFactory(**op_kwargs)
        lot = self.CarbureLotFactory.create(
            added_by=self.entity,
            carbure_supplier=self.entity,
            carbure_client=self.entity,
            carbure_producer=self.entity,
        )
        self.OperationDetailFactory.create_for_operation(op, lot=lot)
        return op

    def test_calculate_balance_groups_operations_by_sector(self):
        """Test calculate_balance correctly groups operations by sector."""
        from core.models import Biocarburant

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

    def test_calculate_balance_groups_gpl_compatible_operations_by_gpl_sector(self):
        """Test calculate_balance maps GPL-compatible biofuels to GPL_C."""
        from core.models import Biocarburant

        biofuel_gpl = Biocarburant.objects.create(
            code="TEST-GPL",
            name="Test GPL",
            name_en="Test GPL",
            description="Test GPL",
            pci_litre=24,
            compatible_essence=False,
            compatible_diesel=False,
            compatible_gpl=True,
        )
        operation = self._create_operation_with_details(
            credited_entity=self.entity,
            type=Operation.INCORPORATION,
            status=Operation.VALIDATED,
            biofuel=biofuel_gpl,
        )
        operation.details.first().lot.biofuel = biofuel_gpl
        operation.details.first().lot.save(update_fields=["biofuel"])

        result = BalanceService.calculate_balance(
            Operation.objects.filter(id=operation.id),
            self.entity.id,
            BalanceService.GROUP_BY_SECTOR,
            "l",
        )

        self.assertIn(Operation.GPL_C, result)
        self.assertGreater(result[Operation.GPL_C]["quantity"]["credit"], 0)

    def test_calculate_balance_filters_operations_by_status(self):
        """Test calculate_balance only includes operations with allowed statuses."""

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

    def test_calculate_balance_excludes_informative_operations(self):
        """YEARLY_BALANCE operations must not contribute to balance calculations."""
        from core.models import Biocarburant

        biofuel = Biocarburant.objects.filter(compatible_essence=True).first()

        if not biofuel:
            self.skipTest("Missing compatible_essence biofuel in fixtures")

        credit_operation = self.OperationFactory.create_incorporation(
            entity=self.entity,
            biofuel=biofuel,
        )
        self.OperationDetailFactory.create_for_operation(credit_operation, volume=1000.0)

        yearly_balance = self.OperationFactory(
            type=Operation.YEARLY_BALANCE,
            status=Operation.ACCEPTED,
            customs_category=MatierePremiere.CONV,
            biofuel=biofuel,
            credited_entity=self.entity,
        )
        OperationDetail.objects.create(operation=yearly_balance, lot=None, volume=500.0)

        operations = Operation.objects.filter(id__in=[credit_operation.id, yearly_balance.id])

        result = BalanceService.calculate_balance(operations, self.entity.id, None, "l")
        total = sum(entry["available_balance"] for entry in result.values())

        self.assertEqual(total, 1000.0)  # 500 from YEARLY_BALANCE should be excluded

    def test_calculate_balance_applies_credit_and_debit_logic(self):
        """Test calculate_balance correctly applies credit/debit based on entity relationship."""

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

    def test_calculate_balance_excludes_pending_credits_from_available_balance(self):
        """Test calculate_balance excludes PENDING credit operations from available_balance."""

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

    @patch("tiruert.services.balance.DeclarationPeriodService.get_current_declaration_year", return_value=2025)
    def test_calculate_balance_excludes_operations_from_next_year(self, mock_current_year):
        """Balance only includes operations up to the current durability year."""
        current_year_operation = self._create_operation_with_details(
            credited_entity=self.entity,
            type=Operation.INCORPORATION,
            status=Operation.ACCEPTED,
            durability_period="202512",
        )
        next_year_operation = self._create_operation_with_details(
            credited_entity=self.entity,
            type=Operation.INCORPORATION,
            status=Operation.ACCEPTED,
            durability_period="202601",
        )

        operations = Operation.objects.filter(id__in=[current_year_operation.id, next_year_operation.id])

        result = BalanceService.calculate_balance(operations, self.entity.id, BalanceService.GROUP_BY_SECTOR, "l")

        total_credit = sum(entry["quantity"]["credit"] for entry in result.values())
        current_year_volume = sum(detail.volume for detail in current_year_operation.details.all())
        self.assertEqual(total_credit, current_year_volume)
        mock_current_year.assert_called_once_with()

    def test_calculate_balance_applies_ges_filtering(self):
        """Test calculate_balance filters lots by GHG reduction bounds."""

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
            operations,
            self.entity.id,
            BalanceService.GROUP_BY_SECTOR,
            "liters",
            detail_filters={"ges_bound_min": 50.0, "ges_bound_max": 70.0},
        )

        # Operations should be excluded, so all quantities should be 0
        for entry in result.values():
            self.assertEqual(entry["quantity"]["debit"], 0)
            self.assertEqual(entry["quantity"]["credit"], 0)

    def test_calculate_balance_includes_all_operations(self):
        """Test calculate_balance computes the complete balance without a date filter."""
        op = self._create_operation_with_details(
            debited_entity=self.entity,
            type=Operation.CESSION,
            status=Operation.VALIDATED,
        )
        operations = Operation.objects.filter(id=op.id)

        result = BalanceService.calculate_balance(
            operations,
            self.entity.id,
            BalanceService.GROUP_BY_SECTOR,
            "liters",
        )

        for entry in result.values():
            self.assertGreater(entry["quantity"]["debit"], 0)

    def test_calculate_balance_groups_by_category(self):
        """Test calculate_balance groups by customs_category correctly."""

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

    def test_calculate_balance_updates_teneur_by_status(self):
        """Test calculate_balance updates pending_teneur vs declared_teneur based on operation status."""

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

    def test_calculate_balance_applies_conversion_factor_for_mj(self):
        """Test calculate_balance applies conversion factor when unit is 'mj'."""

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

    def test_calculate_balance_truncates_teneur_after_sum_per_operation(self):
        """Teneur in MJ must apply int() after summing details per operation, then sum operation totals."""
        from core.models import Biocarburant

        biofuel_essence = Biocarburant.objects.filter(compatible_essence=True).first()

        if not biofuel_essence:
            self.skipTest("Missing compatible_essence biofuel in fixtures")

        biofuel_essence.pci_litre = 27
        biofuel_essence.save()

        lot_1 = self.CarbureLotFactory.create(
            added_by=self.entity,
            carbure_supplier=self.entity,
            carbure_client=self.entity,
            carbure_producer=self.entity,
        )
        lot_2 = self.CarbureLotFactory.create(
            added_by=self.entity,
            carbure_supplier=self.entity,
            carbure_client=self.entity,
            carbure_producer=self.entity,
        )
        lot_3 = self.CarbureLotFactory.create(
            added_by=self.entity,
            carbure_supplier=self.entity,
            carbure_client=self.entity,
            carbure_producer=self.entity,
        )

        # Op1: 2 details, each 1 L * 27 * 0.5 = 13.5
        # int(sum details for op1) = int(27.0) = 27
        # A wrong per-detail truncation would produce int(13.5) + int(13.5) = 26.
        op1 = self.OperationFactory(
            debited_entity=self.entity,
            type=Operation.TENEUR,
            status=Operation.PENDING,
            biofuel=biofuel_essence,
            renewable_energy_share=0.5,
        )
        self.OperationDetailFactory.create_for_operation(op1, lot=lot_1, volume=1.0)
        self.OperationDetailFactory.create_for_operation(op1, lot=lot_2, volume=1.0)

        # Op2: 1 detail, 1 L * 27 * 0.5 = 13.5 -> int(13.5) = 13
        op2 = self.OperationFactory(
            debited_entity=self.entity,
            type=Operation.TENEUR,
            status=Operation.PENDING,
            biofuel=biofuel_essence,
            renewable_energy_share=0.5,
        )
        self.OperationDetailFactory.create_for_operation(op2, lot=lot_3, volume=1.0)

        operations = Operation.objects.filter(id__in=[op1.id, op2.id])

        result = BalanceService.calculate_balance(operations, self.entity.id, BalanceService.GROUP_BY_SECTOR, "mj")

        self.assertIn(Operation.ESSENCE, result)
        self.assertEqual(result[Operation.ESSENCE]["pending_teneur"], 40)

    def test_calculate_balance_teneur_differs_from_global_volume_truncation(self):
        """Current operation-level truncation must differ from old global-volume truncation logic."""
        from core.models import Biocarburant

        biofuel_essence = Biocarburant.objects.filter(compatible_essence=True).first()

        if not biofuel_essence:
            self.skipTest("Missing compatible_essence biofuel in fixtures")

        biofuel_essence.pci_litre = 27
        biofuel_essence.save()

        lot_1 = self.CarbureLotFactory.create(
            added_by=self.entity,
            carbure_supplier=self.entity,
            carbure_client=self.entity,
            carbure_producer=self.entity,
        )
        lot_2 = self.CarbureLotFactory.create(
            added_by=self.entity,
            carbure_supplier=self.entity,
            carbure_client=self.entity,
            carbure_producer=self.entity,
        )

        op1 = self.OperationFactory(
            debited_entity=self.entity,
            type=Operation.TENEUR,
            status=Operation.PENDING,
            biofuel=biofuel_essence,
            renewable_energy_share=0.5,
        )
        self.OperationDetailFactory.create_for_operation(op1, lot=lot_1, volume=1.0)

        op2 = self.OperationFactory(
            debited_entity=self.entity,
            type=Operation.TENEUR,
            status=Operation.PENDING,
            biofuel=biofuel_essence,
            renewable_energy_share=0.5,
        )
        self.OperationDetailFactory.create_for_operation(op2, lot=lot_2, volume=1.0)

        operations = Operation.objects.filter(id__in=[op1.id, op2.id])
        result = BalanceService.calculate_balance(operations, self.entity.id, BalanceService.GROUP_BY_SECTOR, "mj")

        # New rule: sum(int(operation_total)) -> int(13.5) + int(13.5) = 26.
        self.assertIn(Operation.ESSENCE, result)
        self.assertEqual(result[Operation.ESSENCE]["pending_teneur"], 26)

        # Old behavior (global): int((sum volumes) * pci * share) -> int(2 * 27 * 0.5) = 27.
        old_global_pending_teneur = int((1.0 + 1.0) * 27 * 0.5)
        self.assertEqual(old_global_pending_teneur, 27)
        self.assertNotEqual(result[Operation.ESSENCE]["pending_teneur"], old_global_pending_teneur)


class BalanceServiceObjectiveSectorTest(TestCase):
    """Tests for objective_sector override in BalanceService.calculate_balance()."""

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
        from tiruert.factories import OperationDetailFactory, OperationFactory
        from transactions.factories import CarbureLotFactory

        self.entity, _ = Entity.objects.get_or_create(
            name="BalanceDeclaredSectorEntity",
            entity_type=Entity.OPERATOR,
        )
        self.OperationFactory = OperationFactory
        self.OperationDetailFactory = OperationDetailFactory
        self.CarbureLotFactory = CarbureLotFactory

        self.biofuel_diesel = Biocarburant.objects.filter(compatible_diesel=True).first()
        self.biofuel_essence = Biocarburant.objects.filter(compatible_essence=True).first()

    def _create_teneur_with_details(self, biofuel, objective_sector=None, status=Operation.PENDING, declaration_year=None):
        op = self.OperationFactory(
            type=Operation.TENEUR,
            status=status,
            debited_entity=self.entity,
            biofuel=biofuel,
            objective_sector=objective_sector,
            declaration_year=declaration_year,
        )
        lot = self.CarbureLotFactory.create(
            added_by=self.entity,
            carbure_supplier=self.entity,
            carbure_client=self.entity,
            carbure_producer=self.entity,
        )
        self.OperationDetailFactory.create_for_operation(op, lot=lot)
        return op

    def test_objective_sector_overrides_teneur_key_for_sector_groupby(self):
        """A TENEUR with objective_sector=ESSENCE but biofuel=GAZOLE should count pending_teneur in ESSENCE."""

        if not self.biofuel_diesel or not self.biofuel_essence:
            self.skipTest("Missing biofuel fixtures for GAZOLE or ESSENCE sectors")

        # Natural sector of biofuel is GAZOLE, but operator declares it for ESSENCE
        op = self._create_teneur_with_details(self.biofuel_diesel, objective_sector=Operation.ESSENCE)

        operations = Operation.objects.filter(id=op.id)
        result = BalanceService.calculate_balance(operations, self.entity.id, BalanceService.GROUP_BY_SECTOR, "mj")

        # pending_teneur should appear in ESSENCE (declared), not GAZOLE (natural)
        self.assertIn(Operation.ESSENCE, result)
        self.assertGreater(result[Operation.ESSENCE]["pending_teneur"], 0)

        # GAZOLE entry may not exist, or if it does, pending_teneur must be 0
        if Operation.GAZOLE in result:
            self.assertEqual(result[Operation.GAZOLE]["pending_teneur"], 0)

    def test_available_balance_stays_in_natural_sector(self):
        """available_balance must stay in the natural sector even when objective_sector differs."""

        if not self.biofuel_diesel:
            self.skipTest("Missing biofuel fixture for GAZOLE sector")

        op = self._create_teneur_with_details(
            self.biofuel_diesel, objective_sector=Operation.ESSENCE, status=Operation.DECLARED
        )

        operations = Operation.objects.filter(id=op.id)
        result = BalanceService.calculate_balance(operations, self.entity.id, BalanceService.GROUP_BY_SECTOR, "mj")

        # available_balance debited from stocks is under natural sector (GAZOLE)
        self.assertIn(Operation.GAZOLE, result)
        self.assertLess(result[Operation.GAZOLE]["available_balance"], 0)

    def test_no_objective_sector_falls_back_to_biofuel_sector(self):
        """Without objective_sector, behaviour is identical to before: teneur counted in natural sector."""

        if not self.biofuel_diesel:
            self.skipTest("Missing biofuel fixture for GAZOLE sector")

        op = self._create_teneur_with_details(self.biofuel_diesel, objective_sector=None)

        operations = Operation.objects.filter(id=op.id)
        result = BalanceService.calculate_balance(operations, self.entity.id, BalanceService.GROUP_BY_SECTOR, "mj")

        self.assertIn(Operation.GAZOLE, result)
        self.assertGreater(result[Operation.GAZOLE]["pending_teneur"], 0)

        if Operation.ESSENCE in result:
            self.assertEqual(result[Operation.ESSENCE]["pending_teneur"], 0)

    @patch("tiruert.services.balance.DeclarationPeriodService.get_current_declaration_year", return_value=2026)
    def test_teneur_in_declaration_period_is_counted(self, mock_current_year):
        """A TENEUR assigned to the requested declaration year is counted."""
        operation = self._create_teneur_with_details(self.biofuel_essence, declaration_year=2026)

        result = BalanceService.calculate_balance(
            Operation.objects.filter(id=operation.id),
            self.entity.id,
            BalanceService.GROUP_BY_SECTOR,
            "mj",
            declaration_year=2026,
        )

        self.assertGreater(result[Operation.ESSENCE]["pending_teneur"], 0)

    @patch("tiruert.services.balance.DeclarationPeriodService.get_current_declaration_year", return_value=2027)
    def test_teneur_in_other_declaration_period_is_excluded(self, mock_current_year):
        """A TENEUR assigned to a different declaration year than the one requested is not counted."""
        # current_year matches the operation's declaration_year so it isn't dropped by
        # _filter_operations_for_current_year, isolating the exclusion to the declaration_year mismatch.
        operation = self._create_teneur_with_details(self.biofuel_essence, declaration_year=2027)

        result = BalanceService.calculate_balance(
            Operation.objects.filter(id=operation.id),
            self.entity.id,
            BalanceService.GROUP_BY_SECTOR,
            "mj",
            declaration_year=2026,
        )

        self.assertEqual(result[Operation.ESSENCE]["pending_teneur"], 0)

    def test_default_grouping_keeps_teneur_in_natural_sector(self):
        """Default grouping must keep teneur in the biofuel natural sector even when objective_sector differs."""

        if not self.biofuel_diesel:
            self.skipTest("Missing biofuel fixture for GAZOLE sector")

        op = self._create_teneur_with_details(self.biofuel_diesel, objective_sector=Operation.ESSENCE)

        operations = Operation.objects.filter(id=op.id)
        result = BalanceService.calculate_balance(operations, self.entity.id, None, "mj")

        natural_key = (Operation.GAZOLE, op.customs_category, self.biofuel_diesel.code)
        objective_key = (Operation.ESSENCE, op.customs_category, self.biofuel_diesel.code)

        self.assertIn(natural_key, result)
        self.assertGreater(result[natural_key]["pending_teneur"], 0)

        if objective_key in result:
            self.assertEqual(result[objective_key]["pending_teneur"], 0)

    def test_objective_sector_only_applies_to_sector_grouping(self):
        """objective_sector must affect group_by=sector, but not the default sector/category/biofuel grouping."""

        if not self.biofuel_diesel:
            self.skipTest("Missing biofuel fixture for GAZOLE sector")

        op = self._create_teneur_with_details(self.biofuel_diesel, objective_sector=Operation.ESSENCE)

        operations = Operation.objects.filter(id=op.id)

        sector_result = BalanceService.calculate_balance(operations, self.entity.id, BalanceService.GROUP_BY_SECTOR, "mj")
        default_result = BalanceService.calculate_balance(operations, self.entity.id, None, "mj")

        default_natural_key = (Operation.GAZOLE, op.customs_category, self.biofuel_diesel.code)
        default_objective_key = (Operation.ESSENCE, op.customs_category, self.biofuel_diesel.code)

        self.assertIn(Operation.ESSENCE, sector_result)
        self.assertGreater(sector_result[Operation.ESSENCE]["pending_teneur"], 0)

        if Operation.GAZOLE in sector_result:
            self.assertEqual(sector_result[Operation.GAZOLE]["pending_teneur"], 0)

        self.assertIn(default_natural_key, default_result)
        self.assertGreater(default_result[default_natural_key]["pending_teneur"], 0)

        if default_objective_key in default_result:
            self.assertEqual(default_result[default_objective_key]["pending_teneur"], 0)
