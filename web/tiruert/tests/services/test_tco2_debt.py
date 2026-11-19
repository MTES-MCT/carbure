from decimal import ROUND_CEILING, ROUND_DOWN, Decimal
from types import SimpleNamespace

from django.test import TestCase
from rest_framework.exceptions import ValidationError

from core.models import CarbureLot, MatierePremiere
from tiruert.models import Operation, OperationDetail, TiruertDebt
from tiruert.services.correction import CorrectionService
from tiruert.services.debt import DebtService
from tiruert.services.operation import OperationService
from tiruert.tests.debt_utils import DebtTestMixin


def expected_tco2_debt(volume, pci_litre, emission_delta):
    loss = Decimal(str(volume)) * Decimal(str(pci_litre)) * Decimal(str(emission_delta)) / Decimal(1_000_000)
    if loss < Decimal("0.01"):
        return 0.0
    return float(loss.quantize(Decimal("0.01"), rounding=ROUND_DOWN))


class TCO2DebtTest(DebtTestMixin, TestCase):
    def tco2_debt(self, lot, value):
        debt = self.create_debt(lot, value)
        debt.type = TiruertDebt.TCO2
        debt.value = float(Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_DOWN))
        debt.save(update_fields=["type", "value"])
        return debt

    def simulation_data(self, **extra):
        return {
            "biofuel": self.biofuel,
            "customs_category": MatierePremiere.CONV,
            "debited_entity": self.entity,
            **extra,
        }

    def simulate(self, **extra):
        return DebtService.simulate_tco2_repayment(self.simulation_data(**extra))

    def submit(self, preview):
        return OperationService.create_operations(
            SimpleNamespace(entity=self.entity, GET={}),
            {
                **self.simulation_data(),
                "type": Operation.DEBT_REPAYMENT,
                "debt_type": TiruertDebt.TCO2,
            },
            [{"id": lot["lot_id"], "volume": lot["volume"]} for lot in preview["selected_lots"]],
            2026,
        )

    def test_increase_charges_only_initial_sender_and_is_idempotent(self):
        """Only confirmed outgoing transfers of the original credit owner generate debt."""
        lot = self.create_lot()
        transfers = []
        for transfer_status in (
            Operation.ACCEPTED,
            Operation.CORRECTED,
            Operation.PENDING,
            Operation.DRAFT,
            Operation.REJECTED,
            Operation.CANCELED,
        ):
            transfer = Operation.objects.create(
                type=Operation.TRANSFERT,
                status=transfer_status,
                debited_entity=self.entity,
                credited_entity=self.other_entity,
                biofuel=self.biofuel,
                customs_category=MatierePremiere.CONV,
            )
            transfers.append(transfer)
            OperationDetail.objects.create(operation=transfer, lot=lot, volume=100, emission_rate_per_mj=12.5)
        chained = Operation.objects.create(
            type=Operation.TRANSFERT,
            status=Operation.ACCEPTED,
            debited_entity=self.other_entity,
            credited_entity=self.entity,
            biofuel=self.biofuel,
            customs_category=MatierePremiere.CONV,
        )
        OperationDetail.objects.create(operation=chained, lot=lot, volume=100, emission_rate_per_mj=12.5)
        before = {
            operation_id: (volume, rate)
            for operation_id, volume, rate in OperationDetail.objects.filter(operation__in=transfers).values_list(
                "operation_id", "volume", "emission_rate_per_mj"
            )
        }

        def correct(rate):
            CarbureLot.objects.filter(pk=lot.pk).update(ghg_total=rate)
            CorrectionService.create_correction_operations_for_lot_ghg_update([lot.id])

        correct(22.5)
        correct(22.5)
        debt = TiruertDebt.objects.get(type=TiruertDebt.TCO2)
        self.assertEqual(debt.entity, self.entity)
        self.assertEqual(debt.value, expected_tco2_debt(200, self.biofuel.pci_litre, 10))
        for transfer in transfers:
            detail = transfer.details.get()
            with self.subTest(status=transfer.status):
                self.assertEqual((detail.volume, detail.emission_rate_per_mj), before[transfer.id])
                expected_delta = 10 if transfer.status in [Operation.PENDING, Operation.DRAFT] else None
                self.assertEqual(detail.emission_rate_per_mj_delta, expected_delta)
        correct(17.5)
        self.assertEqual(TiruertDebt.objects.count(), 1)
        correct(20)
        self.assertEqual(TiruertDebt.objects.count(), 2)
        self.assertEqual(
            TiruertDebt.objects.order_by("-id").first().value,
            expected_tco2_debt(200, self.biofuel.pci_litre, 2.5),
        )

    def test_simulation_minimizes_liters_and_rounds_up_the_last_centiliter(self):
        """The best tCO2/L lot is consumed first and the final volume rounds upwards."""
        self.create_lot(1000)
        best = self.create_lot(100)
        CarbureLot.objects.filter(pk=best.pk).update(ghg_total=2.5)
        CorrectionService.create_correction_operations_for_lot_ghg_update([best.id])
        self.tco2_debt(best, 0.1)
        preview = self.simulate()
        rate = Decimal("91.5") * Decimal(str(self.biofuel.pci_litre)) / Decimal(1_000_000)
        expected = (Decimal("0.1") / rate).quantize(Decimal("0.01"), rounding=ROUND_CEILING)
        self.assertEqual(preview["selected_lots"], [{"lot_id": best.id, "volume": float(expected)}])
        self.assertGreaterEqual(preview["repaid_tco2"], 0.1)
        self.assertEqual(preview["remaining_tco2"], 0)

    def test_legacy_cession_before_first_transfer_uses_the_actual_initiator(self):
        """A legacy CESSION can make the first transfer sender differ from the original credit owner."""
        lot = self.create_lot()
        for operation_type, sender, recipient in (
            (Operation.CESSION, self.entity, self.other_entity),
            (Operation.TRANSFERT, self.other_entity, self.entity),
            (Operation.TRANSFERT, self.entity, self.other_entity),
        ):
            operation = Operation.objects.create(
                type=operation_type,
                status=Operation.ACCEPTED,
                biofuel=self.biofuel,
                customs_category=MatierePremiere.CONV,
                debited_entity=sender,
                credited_entity=recipient,
            )
            OperationDetail.objects.create(
                operation=operation,
                lot=lot,
                volume=100,
                emission_rate_per_mj=12.5,
            )
        CarbureLot.objects.filter(pk=lot.pk).update(ghg_total=22.5)
        CorrectionService.create_correction_operations_for_lot_ghg_update([lot.id])
        debt = TiruertDebt.objects.get()
        self.assertEqual(debt.entity, self.other_entity)
        self.assertEqual(debt.value, expected_tco2_debt(100, self.biofuel.pci_litre, 10))

    def test_partial_repayment_is_fifo_and_historically_stable(self):
        """TCO2 repayment uses available stock FIFO and survives later GHG corrections."""
        lot = self.create_lot(10)
        first = self.tco2_debt(lot, 0.01)
        second = self.tco2_debt(lot, 1)
        self.create_debt(lot, 20)
        preview = self.simulate()
        self.assertEqual(preview["total_volume"], 10)
        self.assertGreater(preview["remaining_tco2"], 0)
        operations = self.submit(preview)
        self.assertEqual([op.debt_id for op in operations], [first.id, second.id])
        self.assertAlmostEqual(self.remaining(first), 0)
        remaining = self.remaining(second)
        self.assertAlmostEqual(preview["remaining_tco2"], remaining)
        self.assertAlmostEqual(preview["repaid_tco2"] + preview["remaining_tco2"], 1.01)
        self.assertAlmostEqual(self.lot_balance(lot), 0)
        CarbureLot.objects.filter(pk=lot.pk).update(ghg_total=40)
        CorrectionService.create_correction_operations_for_lot_ghg_update([lot.id])
        self.assertEqual(self.remaining(second), remaining)
        summary = DebtService.summarize_open_debts(self.entity.id)
        self.assertEqual(len(summary), 1)
        self.assertEqual(summary[0]["remaining_volume"], 20)
        expected_remaining = float(Decimal(str(remaining)).quantize(Decimal("0.01"), rounding=ROUND_DOWN))
        self.assertEqual(summary[0]["remaining_tco2"], expected_remaining)

    def test_loss_below_two_decimals_does_not_create_debt(self):
        """A GHG increase producing less than 0.01 tCO2 is ignored."""
        lot = self.create_lot()
        transfer = Operation.objects.create(
            type=Operation.TRANSFERT,
            status=Operation.ACCEPTED,
            debited_entity=self.entity,
            credited_entity=self.other_entity,
            biofuel=self.biofuel,
            customs_category=MatierePremiere.CONV,
        )
        OperationDetail.objects.create(operation=transfer, lot=lot, volume=10, emission_rate_per_mj=12.5)
        CarbureLot.objects.filter(pk=lot.pk).update(ghg_total=13.5)
        CorrectionService.create_correction_operations_for_lot_ghg_update([lot.id])
        self.assertFalse(TiruertDebt.objects.filter(type=TiruertDebt.TCO2).exists())

    def test_stale_debt_or_stock_is_rejected_atomically(self):
        """Submitting more than the remaining debt or available stock is rejected atomically."""
        lot = self.create_lot(100)
        debt = self.tco2_debt(lot, 0.1)
        preview = self.simulate()
        original_volume = OperationDetail.objects.get(lot=lot, operation__type=Operation.INCORPORATION).volume
        for change in ("debt", "stock"):
            with self.subTest(change=change):
                try:
                    if change == "debt":
                        debt.value = 0.01
                        debt.save(update_fields=["value"])
                    else:
                        OperationDetail.objects.filter(lot=lot, operation__type=Operation.INCORPORATION).update(volume=1)
                    with self.assertRaises(ValidationError):
                        self.submit(preview)
                    self.assertFalse(Operation.objects.filter(type=Operation.DEBT_REPAYMENT).exists())
                finally:
                    if change == "debt":
                        debt.value = 0.1
                        debt.save(update_fields=["value"])
                    else:
                        OperationDetail.objects.filter(lot=lot, operation__type=Operation.INCORPORATION).update(
                            volume=original_volume
                        )
                preview = self.simulate()

    def test_zero_stock_and_tco2_open_debt_blocking(self):
        """An open TCO2 debt blocks other debits and zero stock gives an explicit error."""
        lot = self.create_lot()
        OperationDetail.objects.filter(lot=lot).update(volume=0)
        self.tco2_debt(lot, 1)
        with self.assertRaises(ValidationError):
            OperationService.check_open_debt(self.entity.id, {**self.simulation_data(), "type": Operation.TRANSFERT})
        with self.assertRaisesMessage(ValidationError, "NO_AVAILABLE_STOCK"):
            self.simulate()

    def test_multiple_debts_round_independently_without_reusing_surplus(self):
        """Each debt needs its own centiliter allocation; rounding surplus is never credited to the next debt."""
        lot = self.create_lot(10)
        first = self.tco2_debt(lot, 0.01)
        second = self.tco2_debt(lot, 0.01)
        preview = self.simulate()
        rate = DebtService._tco2_per_liter(self.biofuel.pci_litre, self.biofuel.renewable_energy_share, 12.5)
        volume_per_debt = (Decimal("0.01") / rate).quantize(Decimal("0.01"), rounding=ROUND_CEILING)
        total_volume = volume_per_debt * 2
        self.assertEqual(preview["selected_lots"], [{"lot_id": lot.id, "volume": float(total_volume)}])
        self.assertEqual(preview["total_volume"], float(total_volume))
        self.assertEqual(preview["repaid_tco2"], 0.02)
        self.assertEqual(preview["remaining_tco2"], 0)
        operations = self.submit(preview)
        self.assertEqual([op.debt_id for op in operations], [first.id, second.id])
        self.assertEqual([op.details.get().volume for op in operations], [float(volume_per_debt)] * 2)
        self.assertEqual(self.remaining(first), 0)
        self.assertEqual(self.remaining(second), 0)
        self.assertAlmostEqual(self.lot_balance(lot), 10 - float(total_volume))

    def test_partial_repayments_accumulate_before_truncating(self):
        """Sub-centitonne contributions carry across partial operations before the balance is truncated."""
        lot = self.create_lot(100)
        debt = self.tco2_debt(lot, 0.01)
        rate = DebtService._tco2_per_liter(self.biofuel.pci_litre, self.biofuel.renewable_energy_share, 12.5)
        volume = (Decimal("0.006") / rate).quantize(Decimal("0.01"), rounding=ROUND_CEILING)
        contribution = volume * rate
        self.assertLess(contribution, Decimal("0.01"))
        self.assertGreaterEqual(contribution * 2, Decimal("0.01"))

        def create_partial_repayment():
            operation = Operation.objects.create(
                type=Operation.DEBT_REPAYMENT,
                status=Operation.VALIDATED,
                biofuel=self.biofuel,
                customs_category=MatierePremiere.CONV,
                debited_entity=self.entity,
                debt=debt,
                renewable_energy_share=self.biofuel.renewable_energy_share,
            )
            OperationDetail.objects.create(
                operation=operation,
                lot=lot,
                volume=float(volume),
                emission_rate_per_mj=12.5,
            )

        create_partial_repayment()
        self.assertLess(self.remaining(debt), 0.01)
        self.assertGreater(self.remaining(debt), 0)
        create_partial_repayment()
        self.assertEqual(self.remaining(debt), 0)

    def test_float_stock_residue_does_not_lose_a_centiliter(self):
        """A business balance of 0.3 - 0.1 L remains 0.2 L, not 0.19 L."""
        lot = self.create_lot(0.3)
        self.create_debt(lot, 0.1)
        self.repay([{"id": lot.id, "volume": 0.1}])
        stock = DebtService._tco2_stock(self.simulation_data())
        self.assertEqual(stock[lot.id][0], Decimal("0.2"))
