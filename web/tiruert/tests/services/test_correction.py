from unittest.mock import patch

from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext

from core.models import Biocarburant, CarbureLot, Entity, MatierePremiere
from tiruert.models import Operation, OperationDetail, TiruertDebt
from tiruert.services.balance import BalanceService
from tiruert.services.correction import CorrectionService
from tiruert.services.operation import OperationService
from transactions.factories import CarbureLotFactory
from transactions.models import Depot


class CorrectionServiceVolumeTest(TestCase):
    fixtures = [
        "json/biofuels.json",
        "json/feedstock.json",
        "json/countries.json",
        "json/depots.json",
        "json/entities.json",
        "json/entities_sites.json",
    ]

    @classmethod
    def setUpTestData(cls):
        cls.entity = Entity.objects.filter(entity_type=Entity.OPERATOR).first()
        cls.depot = Depot.objects.first()
        cls.biofuel_emag = Biocarburant.objects.get(code="EMAG")
        cls.feedstock_conv = MatierePremiere.biofuel.filter(category="CONV").first()

    def create_lot(self, **kwargs):
        lot = CarbureLotFactory.create(
            **{
                "carbure_client": self.entity,
                "feedstock": self.feedstock_conv,
                "biofuel": self.biofuel_emag,
                "lot_status": "ACCEPTED",
                "delivery_type": "BLENDING",
                "volume": 1000,
                "ghg_total": 12.5,
                "carbure_delivery_site": self.depot,
                **kwargs,
            }
        )
        OperationService.create_operations_from_lots(CarbureLot.objects.filter(id=lot.id))
        return lot

    def update_volume(self, lot, volume):
        lot.volume = volume
        lot.save(update_fields=["volume"])
        CorrectionService.create_correction_operations_for_lot_volume_update([lot.id])

    def consume(self, lot, volume, customs_category=None, biofuel=None):
        operation = Operation.objects.create(
            type=Operation.TENEUR,
            status=Operation.ACCEPTED,
            customs_category=customs_category or lot.feedstock.category,
            biofuel=biofuel or lot.biofuel,
            debited_entity=self.entity,
        )
        OperationDetail.objects.create(operation=operation, lot=lot, volume=volume, emission_rate_per_mj=lot.ghg_total)

    def corrections(self):
        return Operation.objects.filter(type=Operation.CORRECTION).order_by("id")

    def repay(self, debt, volume, status=Operation.VALIDATED):
        operation = Operation.objects.create(
            type=Operation.DEBT_REPAYMENT,
            status=status,
            customs_category=debt.customs_category,
            biofuel=debt.biofuel,
            debited_entity=self.entity,
            debt=debt,
        )
        OperationDetail.objects.create(
            operation=operation, lot=debt.lot, volume=volume, emission_rate_per_mj=debt.lot.ghg_total
        )
        return operation

    def create_debt_of_300(self):
        """Consume 800 L then lower the lot to 700 L: the 200 L balance cannot cover the 300 L decrease."""
        lot = self.create_lot()
        self.consume(lot, 800)
        self.update_volume(lot, 700)
        return lot, TiruertDebt.objects.get()

    def test_volume_increase_creates_credit_correction(self):
        """Create a credit correction for volume added to a lot."""
        lot = self.create_lot()

        self.update_volume(lot, 1150)

        correction = self.corrections().get()
        self.assertEqual(correction.status, Operation.VALIDATED)
        self.assertEqual(correction.credited_entity, self.entity)
        self.assertIsNone(correction.debited_entity)
        detail = correction.details.get()
        self.assertEqual(detail.lot_id, lot.id)
        self.assertEqual(detail.volume, 150)
        self.assertEqual(detail.emission_rate_per_mj, lot.ghg_total)

    def test_volume_increase_ignores_lot_balance(self):
        """Create the full volume credit even when the original volume was consumed."""
        lot = self.create_lot()
        self.consume(lot, 1000)

        self.update_volume(lot, 1150)

        correction = self.corrections().get()
        self.assertEqual(correction.credited_entity, self.entity)
        self.assertEqual(correction.details.get().volume, 150)

    def test_volume_decrease_with_insufficient_balance_creates_debt(self):
        """Record the whole decrease as a debt, without any debit, when the lot balance is insufficient."""
        lot = self.create_lot()
        self.consume(lot, 950)

        self.update_volume(lot, 900)

        self.assertFalse(self.corrections().exists())
        debt = TiruertDebt.objects.get()
        self.assertEqual(debt.type, TiruertDebt.VOLUME)
        self.assertEqual(debt.value, 100)
        self.assertEqual(debt.lot_id, lot.id)
        self.assertEqual(debt.entity_id, self.entity.id)
        self.assertEqual(debt.biofuel_id, self.biofuel_emag.id)
        self.assertEqual(debt.customs_category, self.feedstock_conv.category)

    def test_existing_debt_is_not_recreated_by_a_second_correction(self):
        """Running the correction again with the same lot volume leaves the debt unique."""
        lot, debt = self.create_debt_of_300()

        CorrectionService.create_correction_operations_for_lot_volume_update([lot.id])
        CorrectionService.create_correction_operations_for_lot_volume_update([lot.id])

        self.assertEqual(list(TiruertDebt.objects.values_list("id", "value")), [(debt.id, 300)])
        self.assertFalse(self.corrections().exists())

    def test_lot_is_locked_before_tiruert_history_is_read(self):
        """Acquire the lot lock before calculating its TIRUERT correction."""
        if not connection.features.has_select_for_update:
            self.skipTest("The database backend does not support SELECT FOR UPDATE")

        lot = self.create_lot()

        with CaptureQueriesContext(connection) as captured_queries:
            CorrectionService.create_correction_operations_for_lot_volume_update([lot.id])

        queries = [query["sql"].upper() for query in captured_queries]
        lot_table = CarbureLot._meta.db_table.upper()
        detail_table = OperationDetail._meta.db_table.upper()
        lock_index = next(index for index, query in enumerate(queries) if lot_table in query and "FOR UPDATE" in query)
        history_index = next(index for index, query in enumerate(queries) if detail_table in query)

        self.assertLess(lock_index, history_index)

    def test_volume_increase_leaves_existing_debts_untouched(self):
        """Credit the whole increase and keep the open debt unchanged."""
        lot, debt = self.create_debt_of_300()

        self.update_volume(lot, 800)
        self.update_volume(lot, 800)

        debt.refresh_from_db()
        self.assertEqual(debt.value, 300)
        correction = self.corrections().get()
        self.assertEqual(correction.credited_entity, self.entity)
        self.assertEqual(correction.details.get().volume, 100)

    def test_debt_remaining_ignores_inactive_repayments(self):
        """Compute the remaining volume from the active repayments only."""
        _, debt = self.create_debt_of_300()
        self.repay(debt, 100)
        self.repay(debt, 50, status=Operation.CANCELED)

        annotated = TiruertDebt.objects.with_remaining().get()

        self.assertEqual((annotated.repaid, annotated.remaining), (100, 200))

    def test_unchanged_volume_creates_nothing(self):
        """Avoid creating corrections when the converted volume has not changed."""
        lot = self.create_lot(biofuel=Biocarburant.objects.get(code="ETH"))

        CorrectionService.create_correction_operations_for_lot_volume_update([lot.id])
        CorrectionService.create_correction_operations_for_lot_volume_update([lot.id])

        self.assertFalse(self.corrections().exists())

    def test_successive_corrections_only_create_the_remaining_gap(self):
        """Account for previous corrections and create only the remaining volume delta."""
        lot = self.create_lot()

        self.update_volume(lot, 1100)
        self.update_volume(lot, 1100)
        self.update_volume(lot, 1050)

        volumes = [(c.credited_entity_id, c.debited_entity_id, c.details.get().volume) for c in self.corrections()]
        self.assertEqual(volumes, [(self.entity.id, None, 100), (None, self.entity.id, 50)])

    def test_lot_without_initial_operation_is_ignored(self):
        """Ignore volume changes for lots that have no initial TIRUERT credit."""
        lot = CarbureLotFactory.create(
            carbure_client=self.entity,
            feedstock=self.feedstock_conv,
            biofuel=self.biofuel_emag,
            lot_status="DRAFT",
            volume=500,
        )

        self.update_volume(lot, 800)

        self.assertFalse(self.corrections().exists())

    def test_ethanol_volume_conversion_is_applied_to_the_correction(self):
        """Apply the ethanol 15-degree conversion when calculating the volume delta."""
        ethanol = Biocarburant.objects.get(code="ETH")
        lot = self.create_lot(biofuel=ethanol, volume=1000)

        self.update_volume(lot, 2000)

        correction = self.corrections().get()
        self.assertEqual(correction.biofuel, ethanol)
        self.assertEqual(correction.customs_category, self.feedstock_conv.category)
        self.assertEqual(correction.details.get().volume, 995)

    def test_ethanol_volume_decrease_with_insufficient_balance_creates_debt(self):
        """Use ethanol 15-degree volume when recording a debt after a decrease."""
        ethanol = Biocarburant.objects.get(code="ETH")
        lot = self.create_lot(biofuel=ethanol, volume=1000)
        self.consume(lot, 995)

        self.update_volume(lot, 800)

        self.assertFalse(self.corrections().exists())
        debt = TiruertDebt.objects.get()
        self.assertEqual(debt.value, 199)
        self.assertEqual(debt.biofuel, ethanol)
        self.assertEqual(debt.customs_category, self.feedstock_conv.category)
        self.assertEqual(debt.lot_id, lot.id)

    def test_ep2_lot_is_corrected_on_each_category(self):
        """Create separate corrections for both categories produced by an EP2 split."""
        ethanol = Biocarburant.objects.get(code="ETH")
        lot = self.create_lot(
            feedstock=MatierePremiere.biofuel.get(code="EP2"),
            biofuel=ethanol,
            volume=1000,
        )

        self.update_volume(lot, 2000)

        # 1000*0.995 = 995
        # 995 * 0.4 = 398 for CONV
        # 995 * 0.6 = 597 for EP2AM
        deltas = {(c.customs_category, c.biofuel): c.details.get().volume for c in self.corrections()}
        self.assertEqual(deltas, {(MatierePremiere.CONV, ethanol): 398, (MatierePremiere.EP2AM, ethanol): 597})

    def test_ep2_ethanol_decrease_with_insufficient_balance_creates_category_debts(self):
        """Record an insufficient-balance debt for each category after EP2 and ethanol conversion."""
        ethanol = Biocarburant.objects.get(code="ETH")
        lot = self.create_lot(
            feedstock=MatierePremiere.biofuel.get(code="EP2"),
            biofuel=ethanol,
            volume=1000,
        )
        self.consume(lot, 398, customs_category=MatierePremiere.CONV)
        self.consume(lot, 597, customs_category=MatierePremiere.EP2AM)

        self.update_volume(lot, 500)

        self.assertFalse(self.corrections().exists())
        debts = TiruertDebt.objects.order_by("customs_category")

        # 500*0.995 = 497.5
        # 497.5 * 0.4 = 199 for CONV
        # 497.5 * 0.6 = 298.5 for EP2AM
        self.assertEqual(
            [(debt.customs_category, debt.value, debt.biofuel) for debt in debts],
            [(MatierePremiere.CONV, 199, ethanol), (MatierePremiere.EP2AM, 298.5, ethanol)],
        )

    def test_emhv_volume_increase_creates_emag_correction(self):
        """Convert EMHV to EMAG without changing volume before computing the correction."""
        emhv = Biocarburant.objects.get(code="EMHV")
        emag = Biocarburant.objects.get(code="EMAG")
        lot = self.create_lot(biofuel=emhv, volume=1000)

        self.update_volume(lot, 1200)

        correction = self.corrections().get()
        self.assertEqual(correction.biofuel, emag)
        self.assertEqual(correction.customs_category, self.feedstock_conv.category)
        self.assertEqual(correction.details.get().volume, 200)
        lot.refresh_from_db()
        self.assertEqual(lot.biofuel, emhv)

    def test_emhv_volume_decrease_with_insufficient_balance_creates_emag_debt(self):
        """Record the debt under EMAG while leaving the source EMHV lot unchanged."""
        emhv = Biocarburant.objects.get(code="EMHV")
        emag = Biocarburant.objects.get(code="EMAG")
        lot = self.create_lot(biofuel=emhv, volume=1000)
        self.consume(lot, 1000, customs_category=self.feedstock_conv.category, biofuel=emag)

        self.update_volume(lot, 800)

        self.assertFalse(self.corrections().exists())
        debt = TiruertDebt.objects.get()
        self.assertEqual(debt.value, 200)
        self.assertEqual(debt.biofuel, emag)
        self.assertEqual(debt.customs_category, self.feedstock_conv.category)
        self.assertEqual(debt.lot_id, lot.id)
        lot.refresh_from_db()
        self.assertEqual(lot.biofuel, emhv)

    ### GES CORRECTIONS
    def test_ghg_correction_creates_event_from_initial_metadata(self):
        """Create a zero-volume GHG operation with the initial operation's metadata and rates."""
        lot = self.create_lot(ghg_total=20)
        source = Operation.objects.get(type=Operation.INCORPORATION)
        source.renewable_energy_share = 0.5
        source.durability_period = "2024"
        source.declaration_year = 2024
        source.save(update_fields=["renewable_energy_share", "durability_period", "declaration_year"])

        lot.ghg_total = 25
        lot.save(update_fields=["ghg_total"])

        CorrectionService.create_correction_operations_for_lot_ghg_update([lot.id])

        correction = self.corrections().get()
        self.assertEqual(correction.status, Operation.VALIDATED)
        self.assertEqual(
            (
                correction.customs_category,
                correction.biofuel_id,
                correction.credited_entity_id,
                correction.renewable_energy_share,
                correction.durability_period,
                correction.declaration_year,
            ),
            (
                source.customs_category,
                source.biofuel_id,
                source.credited_entity_id,
                source.renewable_energy_share,
                source.durability_period,
                source.declaration_year,
            ),
        )
        detail = correction.details.get()
        self.assertEqual(
            (detail.lot_id, detail.volume, detail.emission_rate_per_mj, detail.emission_rate_per_mj_delta),
            (lot.id, 0, 20, 5),
        )

    def test_ghg_correction_updates_existing_credit_details(self):
        """Correct initial incorporation and previous volume correction without replacing their historical rates."""
        lot = self.create_lot(ghg_total=20)
        self.update_volume(lot, 1100)

        original = Operation.objects.get(type=Operation.INCORPORATION)
        volume_correction = self.corrections().get()

        lot.ghg_total = 25
        lot.save(update_fields=["ghg_total"])

        CorrectionService.create_correction_operations_for_lot_ghg_update([lot.id])

        for operation in (original, volume_correction):
            with self.subTest(operation_id=operation.pk):
                operation.refresh_from_db()
                self.assertEqual(operation.status, Operation.CORRECTED)
                detail = operation.details.get()
                self.assertEqual(detail.emission_rate_per_mj, 20)
                self.assertEqual(detail.emission_rate_per_mj_delta, 5)

    def test_ghg_correction_preserves_historical_balance(self):
        """A GHG correction changes neither balance nor historical saved emissions."""
        lot = self.create_lot(ghg_total=20)
        self.consume(lot, 100)
        before = BalanceService.calculate_balance(Operation.objects.all(), self.entity.id, None, "l")
        lot.ghg_total = 25
        lot.save(update_fields=["ghg_total"])

        CorrectionService.create_correction_operations_for_lot_ghg_update([lot.id])

        after = BalanceService.calculate_balance(Operation.objects.all(), self.entity.id, None, "l")
        self.assertEqual(after.keys(), before.keys())
        before_entry = next(iter(before.values()))
        after_entry = next(iter(after.values()))
        self.assertEqual(after_entry["available_balance"], before_entry["available_balance"])
        self.assertAlmostEqual(after_entry["saved_emissions"], before_entry["saved_emissions"])

    def test_ghg_correction_ignores_unconfirmed_credits(self):
        """Unconfirmed or inactive incorporation must not produce GHG corrections."""
        lot = self.create_lot(ghg_total=20)
        source = Operation.objects.get(type=Operation.INCORPORATION)
        lot.ghg_total = 25
        lot.save(update_fields=["ghg_total"])

        for operation_status in (Operation.DRAFT, Operation.PENDING, Operation.CANCELED, Operation.REJECTED):
            with self.subTest(status=operation_status):
                source.status = operation_status
                source.save(update_fields=["status"])

                CorrectionService.create_correction_operations_for_lot_ghg_update([lot.id])

                source.refresh_from_db()
                self.assertEqual(source.status, operation_status)
                self.assertIsNone(source.details.get().emission_rate_per_mj_delta)
                self.assertFalse(self.corrections().exists())

    def test_combined_update_rolls_back_ghg_when_volume_correction_fails(self):
        """A failed volume correction rolls back the GHG event and source changes."""
        lot = self.create_lot(ghg_total=20)
        source = Operation.objects.get(type=Operation.INCORPORATION)
        lot.ghg_total = 25
        lot.volume = 1200
        lot.save(update_fields=["ghg_total", "volume"])

        with patch.object(
            CorrectionService, "_create_volume_correction", side_effect=ValueError("Volume correction failed")
        ):
            with self.assertRaisesMessage(ValueError, "Volume correction failed"):
                CorrectionService.create_correction_operations_for_lot_update([lot.id])

        source.refresh_from_db()
        self.assertEqual(source.status, Operation.VALIDATED)
        self.assertIsNone(source.details.get().emission_rate_per_mj_delta)
        self.assertFalse(self.corrections().exists())

    def test_successive_ghg_corrections_keep_each_event_immutable(self):
        """Keep event deltas immutable and the source delta relative to its creation rate."""
        lot = self.create_lot(ghg_total=20)
        for rate in (25, 25, 22, 20):
            lot.ghg_total = rate
            lot.save(update_fields=["ghg_total"])
            CorrectionService.create_correction_operations_for_lot_update([lot.id])

        details = OperationDetail.objects.filter(operation__type=Operation.CORRECTION).order_by("id")
        self.assertEqual(
            list(details.values_list("volume", "emission_rate_per_mj", "emission_rate_per_mj_delta")),
            [(0, 20, 5), (0, 25, -3), (0, 22, -2)],
        )
        original = Operation.objects.get(type=Operation.INCORPORATION)
        self.assertEqual(original.status, Operation.CORRECTED)
        self.assertEqual(original.details.get().emission_rate_per_mj_delta, 0)
        self.assertEqual(original.corrected_avoided_emissions, original.avoided_emissions)

    def test_ghg_correction_keeps_existing_debits_and_other_lots_unchanged(self):
        """Correct only the changed lot's source details, not historical debits or neighbouring lots."""
        lot = self.create_lot(ghg_total=20)
        self.consume(lot, 100)

        original = Operation.objects.get(type=Operation.INCORPORATION)
        other_lot = CarbureLotFactory.create(biofuel=self.biofuel_emag, ghg_total=30)
        other_detail = OperationDetail.objects.create(operation=original, lot=other_lot, volume=500, emission_rate_per_mj=30)

        lot.ghg_total = 10
        lot.save(update_fields=["ghg_total"])

        CorrectionService.create_correction_operations_for_lot_ghg_update([lot.id])

        other_detail.refresh_from_db()
        self.assertIsNone(other_detail.emission_rate_per_mj_delta)
        debit = Operation.objects.get(type=Operation.TENEUR)
        self.assertEqual(debit.status, Operation.ACCEPTED)
        self.assertIsNone(debit.details.get().emission_rate_per_mj_delta)
        self.assertIsNone(debit.corrected_avoided_emissions)
        original.refresh_from_db()
        self.assertGreater(original.corrected_avoided_emissions, original.avoided_emissions)

    def test_combined_update_creates_volume_at_new_validated_rate(self):
        """Create the new volume correction at the newly validated rate, without a historical delta."""
        lot = self.create_lot(ghg_total=20)
        lot.ghg_total = 25
        lot.volume = 1200
        lot.save(update_fields=["ghg_total", "volume"])

        CorrectionService.create_correction_operations_for_lot_update([lot.id])
        CorrectionService.create_correction_operations_for_lot_update([lot.id])

        self.assertEqual(self.corrections().count(), 2)
        volume_correction = self.corrections().get(details__volume=200)
        self.assertEqual(volume_correction.status, Operation.VALIDATED)
        self.assertEqual(volume_correction.details.get().emission_rate_per_mj, 25)
        self.assertIsNone(volume_correction.details.get().emission_rate_per_mj_delta)
        self.assertIsNone(volume_correction.ghg_delta)

    def test_future_rate_ignores_unapproved_lot_changes_and_old_debits(self):
        """Use the source's last validated GES rather than the mutable lot"""
        lot = self.create_lot(ghg_total=20)
        self.consume(lot, 100)

        lot.ghg_total = 25
        lot.save(update_fields=["ghg_total"])

        CorrectionService.create_correction_operations_for_lot_ghg_update([lot.id])

        lot.ghg_total = 30
        lot.save(update_fields=["ghg_total"])

        self.assertEqual(OperationService.get_emission_rates_by_lot([lot.id]), {lot.id: 25})

        balance = BalanceService.calculate_balance(Operation.objects.all(), self.entity.id, BalanceService.GROUP_BY_LOT, "l")
        self.assertEqual(next(iter(balance.values()))["emission_rate_per_mj"], 25)

    def test_zero_and_negative_ghg_rates_are_valid(self):
        """Preserve zero and negative intensities rather than treating them as missing values."""
        lot = self.create_lot(ghg_total=20)
        for rate in (0, -5):
            lot.ghg_total = rate
            lot.save(update_fields=["ghg_total"])
            CorrectionService.create_correction_operations_for_lot_ghg_update([lot.id])
            self.assertEqual(OperationService.get_emission_rates_by_lot([lot.id]), {lot.id: rate})
