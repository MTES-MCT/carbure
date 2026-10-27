from django.test import SimpleTestCase, TestCase
from rest_framework.exceptions import ValidationError

from core.models import MatierePremiere
from tiruert.models import Operation, TiruertDebt
from tiruert.services.debt import DebtService
from tiruert.tests.debt_utils import DebtTestMixin


class DebtServiceGetOpenDebtsTest(DebtTestMixin, TestCase):
    def test_returns_only_open_volume_debts_of_the_entity_oldest_first(self):
        """Closed debts, TCO2 debts and debts of other entities are ignored; order is created_at then id."""
        lot = self.create_lot()
        other_lot = self.create_lot(entity=self.other_entity)
        first = self.create_debt(lot, 100)
        second = self.create_debt(lot, 70)
        self.create_debt(other_lot, 30, entity=self.other_entity)
        TiruertDebt.objects.create(
            type=TiruertDebt.TCO2,
            value=5,
            entity=self.entity,
            biofuel=self.biofuel,
            customs_category=MatierePremiere.CONV,
            lot=lot,
        )
        self.assertEqual([debt.id for debt in DebtService.get_open_debts(self.entity.id)], [first.id, second.id])

        DebtService.repay(self.entity, self.biofuel, MatierePremiere.CONV, [{"id": lot.id, "volume": 100}])

        self.assertEqual([debt.id for debt in DebtService.get_open_debts(self.entity.id)], [second.id])

    def test_filters_by_biofuel_and_customs_category(self):
        """The optional biofuel and customs category narrow the result."""
        lot = self.create_lot()
        debt = self.create_debt(lot, 100)

        self.assertEqual(list(DebtService.get_open_debts(self.entity.id, self.biofuel.id, MatierePremiere.CONV)), [debt])
        self.assertEqual(list(DebtService.get_open_debts(self.entity.id, customs_category=MatierePremiere.IXA)), [])
        self.assertEqual(list(DebtService.get_open_debts(self.entity.id, biofuel_id=self.biofuel.id + 1000)), [])


class DebtServiceSummarizeTest(DebtTestMixin, TestCase):
    def test_sums_remaining_by_biofuel_and_category_for_the_entity_only(self):
        """Remaining volumes are summed per (biofuel, customs_category), other entities are excluded."""
        lot = self.create_lot()
        other_lot = self.create_lot(entity=self.other_entity)
        self.create_debt(lot, 300)
        self.create_debt(lot, 200)
        self.create_debt(other_lot, 999, entity=self.other_entity)
        DebtService.repay(self.entity, self.biofuel, MatierePremiere.CONV, [{"id": lot.id, "volume": 120.5}])

        with self.assertNumQueries(2):
            summary = DebtService.summarize_open_debts(self.entity.id)

        self.assertEqual(len(summary), 1)
        self.assertEqual(summary[0]["biofuel"], self.biofuel)
        self.assertEqual(summary[0]["customs_category"], MatierePremiere.CONV)
        self.assertEqual(summary[0]["remaining_volume"], 379.5)

    def test_returns_nothing_without_open_debt(self):
        """No open debt gives an empty summary."""
        self.assertEqual(DebtService.summarize_open_debts(self.entity.id), [])


class DebtServiceSplitLotsBetweenDebtsTest(SimpleTestCase):
    split = staticmethod(DebtService._split_lots_between_debts)

    def test_a_lot_covering_a_debt_exactly_is_used_up(self):
        """A lot equal to the debt goes entirely to it and the next debt takes the next lot."""
        self.assertEqual(self.split({1: 100, 2: 50}, {10: 100, 11: 50}), {10: {1: 100}, 11: {2: 50}})

    def test_a_lot_is_split_between_two_debts(self):
        """The leftover of a lot is used by the next debt before moving on to the next lot."""
        self.assertEqual(
            self.split({1: 250, 2: 250}, {10: 300, 11: 200}),
            {10: {1: 250, 2: 50}, 11: {2: 200}},
        )

    def test_a_debt_is_filled_by_several_lots(self):
        """Several lots are combined, in order, to fill one debt."""
        self.assertEqual(self.split({1: 30, 2: 40, 3: 50}, {10: 100}), {10: {1: 30, 2: 40, 3: 30}})

    def test_debts_left_without_volume_are_omitted(self):
        """Debts beyond the volume of the lots get no entry (partial repayment)."""
        self.assertEqual(self.split({1: 120}, {10: 100, 11: 80, 12: 60}), {10: {1: 100}, 11: {1: 20}})

    def test_surplus_volume_of_the_lots_is_ignored(self):
        """The lots volume above the total debt is not allocated."""
        self.assertEqual(self.split({1: 100, 2: 100}, {10: 50}), {10: {1: 50}})

    def test_nothing_to_split(self):
        """No lot or no debt gives an empty split."""
        self.assertEqual(self.split({}, {10: 100}), {})
        self.assertEqual(self.split({1: 100}, {}), {})

    def test_float_residue_does_not_leave_a_phantom_remainder(self):
        """0.3 - 0.1 is 0.19999999999999998 in floats: volumes are still allocated as 0.1 then 0.2."""
        self.assertEqual(self.split({1: 0.3}, {10: 0.1, 11: 0.2}), {10: {1: 0.1}, 11: {1: 0.2}})
        self.assertEqual(self.split({1: 0.1, 2: 0.2}, {10: 0.3}), {10: {1: 0.1, 2: 0.2}})


class DebtServiceRepayTest(DebtTestMixin, TestCase):
    def repay(self, lots, entity=None):
        return DebtService.repay(entity or self.entity, self.biofuel, MatierePremiere.CONV, lots)

    def test_repay_spreads_volumes_oldest_debt_first_and_splits_a_lot(self):
        """Lots are consumed in order over the debts, a lot can be split between two debts."""
        lot_a = self.create_lot(1000)
        lot_b = self.create_lot(500)
        debt_1 = self.create_debt(lot_a, 300)
        debt_2 = self.create_debt(lot_a, 200)

        operations = self.repay([{"id": lot_a.id, "volume": 250}, {"id": lot_b.id, "volume": 250}])

        self.assertEqual(len(operations), 2)
        first, second = operations
        self.assertEqual(first.debt_id, debt_1.id)
        self.assertEqual(second.debt_id, debt_2.id)
        self.assertEqual({d.lot_id: d.volume for d in first.details.all()}, {lot_a.id: 250, lot_b.id: 50})
        self.assertEqual({d.lot_id: d.volume for d in second.details.all()}, {lot_b.id: 200})
        self.assertEqual(self.remaining(debt_1), 0)
        self.assertEqual(self.remaining(debt_2), 0)

    def test_repay_creates_validated_debit_operations_without_recipient(self):
        """The operation debits the entity, has no recipient and carries the biofuel renewable share."""
        lot = self.create_lot()
        self.create_debt(lot, 100)

        (operation,) = self.repay([{"id": lot.id, "volume": 100}])

        self.assertEqual(operation.type, Operation.DEBT_REPAYMENT)
        self.assertEqual(operation.status, Operation.VALIDATED)
        self.assertEqual(operation.debited_entity, self.entity)
        self.assertIsNone(operation.credited_entity)
        self.assertEqual(operation.customs_category, MatierePremiere.CONV)
        self.assertEqual(operation.biofuel, self.biofuel)
        self.assertEqual(operation.renewable_energy_share, self.biofuel.renewable_energy_share)
        self.assertIsNotNone(operation.declaration_year)
        self.assertEqual(operation.details.get().emission_rate_per_mj, 12.5)

    def test_repay_is_capped_to_the_remaining_debt(self):
        """Repaying more than the remaining debt is refused and nothing is created."""
        lot = self.create_lot()
        debt = self.create_debt(lot, 100)

        with self.assertRaises(ValidationError) as error:
            self.repay([{"id": lot.id, "volume": 100.01}])

        self.assertIn("volume", error.exception.detail)
        self.assertEqual(Operation.objects.filter(type=Operation.DEBT_REPAYMENT).count(), 0)
        self.assertEqual(self.remaining(debt), 100)

    def test_partial_then_full_repayment_reduces_the_remaining_volume(self):
        """`remaining` follows the repayments until the debt is closed and leaves the open debts."""
        lot = self.create_lot()
        debt = self.create_debt(lot, 300)

        self.repay([{"id": lot.id, "volume": 100.1}])
        self.assertAlmostEqual(self.remaining(debt), 199.9)
        self.assertEqual([d.id for d in DebtService.get_open_debts(self.entity.id)], [debt.id])

        self.repay([{"id": lot.id, "volume": 199.9}])
        self.assertEqual(DebtService.get_open_debts(self.entity.id).count(), 0)
        self.assertEqual(debt.repayments.count(), 2)

    def test_volume_above_the_lot_balance_is_refused(self):
        """A lot cannot be debited beyond its available balance, even if the debt is larger."""
        lot = self.create_lot(500)
        self.create_debt(lot, 1000)

        with self.assertRaises(ValidationError) as error:
            self.repay([{"id": lot.id, "volume": 600}])

        self.assertIn("volume", error.exception.detail)
        self.assertEqual(Operation.objects.filter(type=Operation.DEBT_REPAYMENT).count(), 0)

    def test_lots_of_another_entity_are_refused(self):
        """Only lots with a balance for the repaying entity can be used."""
        lot = self.create_lot()
        foreign_lot = self.create_lot(entity=self.other_entity)
        self.create_debt(lot, 100)

        with self.assertRaises(ValidationError) as error:
            self.repay([{"id": foreign_lot.id, "volume": 50}])

        self.assertIn("lot_id", error.exception.detail)
        self.assertEqual(Operation.objects.filter(type=Operation.DEBT_REPAYMENT).count(), 0)

    def test_canceled_repayment_is_ignored_in_the_remaining_volume(self):
        """A canceled repayment no longer counts, the debt is open again and the lot balance is back."""
        lot = self.create_lot()
        debt = self.create_debt(lot, 100)
        (operation,) = self.repay([{"id": lot.id, "volume": 100}])
        self.assertEqual(self.remaining(debt), 0)

        operation.status = Operation.CANCELED
        operation.save(update_fields=["status"])

        self.assertEqual(self.remaining(debt), 100)
        self.assertEqual([d.id for d in DebtService.get_open_debts(self.entity.id)], [debt.id])
        self.assertEqual(self.lot_balance(lot), 1000)

    def test_repay_without_open_debt_is_refused(self):
        """Without any open debt for the couple there is nothing to repay."""
        lot = self.create_lot()

        with self.assertRaises(ValidationError) as error:
            self.repay([{"id": lot.id, "volume": 10}])

        self.assertIn("debt", error.exception.detail)

    def test_non_positive_volume_is_refused(self):
        """Zero, negative and sub-centiliter volumes are refused."""
        lot = self.create_lot()
        self.create_debt(lot, 100)

        for volume in (0, -10, 0.004):
            with self.subTest(volume=volume), self.assertRaises(ValidationError) as error:
                self.repay([{"id": lot.id, "volume": volume}])
            self.assertIn("volume", error.exception.detail)

    def test_same_lot_given_twice_is_summed(self):
        """Duplicated lot ids are merged before checking the balance."""
        lot = self.create_lot(500)
        self.create_debt(lot, 1000)

        with self.assertRaises(ValidationError):
            self.repay(
                [{"id": lot.id, "volume": 300}, {"id": lot.id, "volume": 300}]
            )  # should raise because total volume (600) exceeds lot balance (500)

        (operation,) = self.repay([{"id": lot.id, "volume": 200}, {"id": lot.id, "volume": 100}])
        self.assertEqual([d.volume for d in operation.details.all()], [300])

    def test_float_residue_does_not_leave_an_open_debt(self):
        """Debts of 0.1 L and 0.2 L repaid by 0.1 + 0.2 L are both closed, without a residue of 1e-17 L."""
        lot = self.create_lot()
        first = self.create_debt(lot, 0.1)
        second = self.create_debt(lot, 0.2)

        operations = self.repay([{"id": lot.id, "volume": 0.1}, {"id": lot.id, "volume": 0.2}])

        self.assertEqual([op.debt_id for op in operations], [first.id, second.id])
        self.assertEqual(DebtService.get_open_debts(self.entity.id).count(), 0)
        self.assertEqual(DebtService.summarize_open_debts(self.entity.id), [])

    def test_volumes_are_truncated_to_two_decimals(self):
        """A volume with three decimals is truncated, so 100.129 L closes a debt of 100.12 L."""
        lot = self.create_lot()
        debt = self.create_debt(lot, 100.12)

        (operation,) = self.repay([{"id": lot.id, "volume": 100.129}])

        self.assertEqual(operation.details.get().volume, 100.12)
        self.assertEqual(self.remaining(debt), 0)
        self.assertEqual(DebtService.get_open_debts(self.entity.id).count(), 0)

    def test_repay_decreases_the_lot_balance(self):
        """A repayment debits the lot like any other debit."""
        lot = self.create_lot(1000)
        self.create_debt(lot, 400)
        self.assertEqual(self.lot_balance(lot), 1000)

        self.repay([{"id": lot.id, "volume": 150.25}])

        self.assertAlmostEqual(self.lot_balance(lot), 849.75)

    def test_repay_with_draft_status_creates_drafts_that_reserve_the_volume(self):
        """status=DRAFT creates DRAFT operations, the remaining debt and the lot balance decrease like for VALIDATED."""
        lot = self.create_lot(1000)
        debt = self.create_debt(lot, 300)

        operations = DebtService.repay(
            self.entity, self.biofuel, MatierePremiere.CONV, [{"id": lot.id, "volume": 120}], status=Operation.DRAFT
        )

        self.assertEqual([operation.status for operation in operations], [Operation.DRAFT])
        self.assertEqual(self.remaining(debt), 180)
        self.assertEqual(self.lot_balance(lot), 880)

    def test_draft_repayment_keeps_the_volume_checks(self):
        """A draft cannot exceed the remaining debt nor the lot balance."""
        lot = self.create_lot(500)
        self.create_debt(lot, 1000)

        for volume in (600, 1100):
            with self.subTest(volume=volume), self.assertRaises(ValidationError):
                DebtService.repay(
                    self.entity,
                    self.biofuel,
                    MatierePremiere.CONV,
                    [{"id": lot.id, "volume": volume}],
                    status=Operation.DRAFT,
                )
        self.assertEqual(Operation.objects.filter(type=Operation.DEBT_REPAYMENT).count(), 0)
