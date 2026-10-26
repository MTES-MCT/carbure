from django.test import TestCase

from core.models import Biocarburant, CarbureLot, Entity, MatierePremiere
from tiruert.models import Operation, OperationDetail
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

    def consume(self, lot, volume):
        operation = Operation.objects.create(
            type=Operation.TENEUR,
            status=Operation.ACCEPTED,
            customs_category=lot.feedstock.category,
            biofuel=lot.biofuel,
            debited_entity=self.entity,
        )
        OperationDetail.objects.create(operation=operation, lot=lot, volume=volume, emission_rate_per_mj=lot.ghg_total)

    def corrections(self):
        return Operation.objects.filter(type=Operation.CORRECTION).order_by("id")

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

    def test_volume_decrease_with_enough_balance_creates_debit_correction(self):
        """Create a debit correction when the remaining balance covers the decrease."""
        lot = self.create_lot()
        self.consume(lot, 400)

        self.update_volume(lot, 700)

        correction = self.corrections().get()
        self.assertEqual(correction.debited_entity, self.entity)
        self.assertIsNone(correction.credited_entity)
        self.assertEqual(correction.details.get().volume, 300)

    def test_volume_decrease_with_insufficient_balance_creates_nothing(self):
        """Leave the decrease uncorrected when the lot balance is insufficient."""
        lot = self.create_lot()
        self.consume(lot, 800)

        self.update_volume(lot, 700)

        self.assertFalse(self.corrections().exists())

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
        lot = self.create_lot(biofuel=Biocarburant.objects.get(code="ETH"), volume=1000)

        self.update_volume(lot, 2000)

        self.assertEqual(self.corrections().get().details.get().volume, 995)

    def test_ep2_lot_is_corrected_on_each_category(self):
        """Create separate corrections for both categories produced by an EP2 split."""
        lot = self.create_lot(
            feedstock=MatierePremiere.biofuel.get(code="EP2"),
            biofuel=Biocarburant.objects.get(code="ETH"),
            volume=1000,
        )

        self.update_volume(lot, 2000)

        deltas = {c.customs_category: c.details.get().volume for c in self.corrections()}
        self.assertEqual(deltas, {MatierePremiere.CONV: 398, MatierePremiere.EP2AM: 597})
