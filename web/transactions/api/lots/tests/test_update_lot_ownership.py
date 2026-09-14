from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from core.models import Biocarburant, CarbureLot, CarbureLotEvent, Entity, GenericError, UserRights
from core.tests_utils import setup_current_user
from transactions.factories import CarbureLotFactory, CarbureStockFactory


class TestUpdateLotOwnership(TestCase):
    """A foreign entity must not mutate a lot, its parent stock, errors or events.

    The update endpoint only checks UserRights on entity_id. Without an added_by
    check, enforce_stock_integrity() used to save the parent stock before
    LotNode.update() rejected the request.
    """

    fixtures = [
        "json/biofuels.json",
        "json/feedstock.json",
        "json/countries.json",
        "json/depots.json",
        "json/entities.json",
        "json/entities_sites.json",
    ]

    def setUp(self):
        self.owner = Entity.objects.filter(entity_type=Entity.PRODUCER).first()
        self.attacker = Entity.objects.filter(entity_type=Entity.TRADER).first()
        self.eth = Biocarburant.objects.get(code="ETH")

        setup_current_user(
            self,
            email="attacker@carbure.local",
            name="Attacker",
            password="gogogo",
            entity_rights=[(self.attacker, UserRights.RW)],
        )

        parent_lot = CarbureLotFactory.create(
            lot_status=CarbureLot.ACCEPTED,
            delivery_type=CarbureLot.STOCK,
            added_by=self.owner,
            carbure_client=self.owner,
            carbure_supplier=self.owner,
            carbure_producer=self.owner,
            biofuel=self.eth,
            volume=50000,
        )
        self.stock = CarbureStockFactory.create(
            parent_lot=parent_lot,
            carbure_client=self.owner,
            biofuel=self.eth,
            remaining_volume=40000,
            remaining_weight=40000,
            remaining_lhv_amount=40000,
        )
        self.lot = CarbureLotFactory.create(
            lot_status=CarbureLot.DRAFT,
            added_by=self.owner,
            parent_stock=self.stock,
            carbure_client=self.owner,
            carbure_supplier=self.owner,
            biofuel=self.eth,
            volume=10000,
            weight=10000,
            lhv_amount=10000,
            free_field="original",
        )

    def test_cannot_update_another_entity_lot_or_its_stock(self):
        error_count = GenericError.objects.filter(lot=self.lot).count()
        event_count = CarbureLotEvent.objects.filter(lot=self.lot).count()

        response = self.client.post(
            reverse("transactions-lots-update"),
            {
                "entity_id": self.attacker.id,
                "lot_id": self.lot.id,
                "volume": 5000,
            },
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.lot.refresh_from_db()
        self.stock.refresh_from_db()

        self.assertEqual(self.lot.volume, 10000)
        self.assertEqual(self.lot.weight, 10000)
        self.assertEqual(self.lot.lhv_amount, 10000)
        self.assertEqual(self.lot.free_field, "original")
        self.assertEqual(self.lot.added_by_id, self.owner.id)

        self.assertEqual(self.stock.remaining_volume, 40000)
        self.assertEqual(self.stock.remaining_weight, 40000)
        self.assertEqual(self.stock.remaining_lhv_amount, 40000)
        self.assertEqual(self.stock.carbure_client_id, self.owner.id)

        self.assertEqual(GenericError.objects.filter(lot=self.lot).count(), error_count)
        self.assertEqual(CarbureLotEvent.objects.filter(lot=self.lot).count(), event_count)
        self.assertFalse(CarbureLotEvent.objects.filter(lot=self.lot, entity=self.attacker).exists())
