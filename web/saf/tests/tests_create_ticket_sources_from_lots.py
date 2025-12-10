from unittest import TestCase

from core.models import Biocarburant, CarbureLot, Entity
from entity.factories.entity import EntityFactory
from saf.models.saf_ticket_source import create_ticket_sources_from_lots
from transactions.factories.carbure_lot import CarbureLotFactory


class CreateTicketSourcesFromLotsTest(TestCase):
    fixtures = [
        "json/biofuels.json",
        "json/feedstock.json",
        "json/countries.json",
        "json/depots.json",
        "json/entities.json",
        "json/productionsites.json",
        "json/entities_sites.json",
    ]

    @classmethod
    def setUpClass(cls):
        cls.entity = EntityFactory.create(entity_type=Entity.OPERATOR, has_saf=True)
        cls.hvoc = Biocarburant.objects.get(code="HVOC")
        cls.eth = Biocarburant.objects.get(code="ETH")

    def create_lot(self, **kwargs):
        params = {
            "biofuel": self.hvoc,
            "carbure_client": self.entity,
            "lot_status": CarbureLot.ACCEPTED,
            "delivery_type": CarbureLot.BLENDING,
            **kwargs,
        }
        return CarbureLotFactory.create(**params)

    def test_only_valid_saf_lots_are_turned_into_ticket_source(self):
        valid_lot_1 = self.create_lot(delivery_type=CarbureLot.DIRECT)
        valid_lot_2 = self.create_lot(lot_status=CarbureLot.FROZEN)

        self.create_lot(biofuel=self.eth)  # ignored biofuel
        self.create_lot(lot_status=CarbureLot.PENDING)  # ignored status
        self.create_lot(delivery_type=CarbureLot.EXPORT)  # ignored delivery type

        lots = CarbureLot.objects.filter(carbure_client=self.entity)
        ticket_sources = create_ticket_sources_from_lots(lots)

        self.assertEqual(len(ticket_sources), 2)
        self.assertEqual(ticket_sources[0].parent_lot_id, valid_lot_1.id)
        self.assertEqual(ticket_sources[1].parent_lot_id, valid_lot_2.id)
