from django.test import TestCase

from api.v4.tests_utils import setup_current_user
from core.traceability_tree import LotNode, StockNode, StockTransformNode, TicketSourceNode, TicketNode
from core.models import Entity, CarbureLot, CarbureStock, CarbureStockTransformation
from saf.models import SafTicket, SafTicketSource
from transactions.factories import CarbureLotFactory, CarbureStockFactory, CarbureStockTransformFactory
from saf.factories import SafTicketSourceFactory, SafTicketFactory


class TraceabilityTest(TestCase):
    fixtures = [
        "json/biofuels.json",
        "json/feedstock.json",
        "json/countries.json",
        "json/entities.json",
        "json/productionsites.json",
        "json/depots.json",
    ]

    def setUp(self):
        self.entity = Entity.objects.filter(entity_type=Entity.OPERATOR)[0]
        self.user = setup_current_user(self, "tester@carbure.local", "Tester", "gogogo", [(self.entity, "ADMIN")])

        CarbureLot.objects.all().delete()
        CarbureStock.objects.all().delete()
        CarbureStockTransformation.objects.all().delete()
        SafTicketSource.objects.all().delete()
        SafTicket.objects.all().delete()

    def test_traceability_single_lot(self):
        lot = CarbureLotFactory.create()
        node = LotNode(lot)

        self.assertEqual(node.get_depth(), 0)
        self.assertEqual(len(node.children), 0)

        node.update({"carbure_id": "ABCD"})
        self.assertEqual(lot.carbure_id, "ABCD")

    def test_traceability_lot_to_lot(self):
        parent_lot = CarbureLotFactory.create(added_by=self.entity)
        CarbureLotFactory.create(parent_lot=parent_lot, added_by=self.entity)

        parent_node = LotNode(parent_lot)
        child_node = parent_node.get_first(LotNode)

        self.assertEqual(parent_node.get_depth(), 0)
        self.assertEqual(child_node.get_depth(), 1)

        self.assertEqual(len(parent_node.children), 1)
        self.assertEqual(child_node.parent, parent_node)

        parent_node.update({"transport_document_reference": "ABCD", "unknown_delivery_site": "UNKNOWN", "esca": 2.0})
        self.assertEqual(parent_node.data.transport_document_reference, "ABCD")
        self.assertEqual(parent_node.data.unknown_delivery_site, "UNKNOWN")
        self.assertEqual(parent_node.data.esca, 2.0)

        original_child_unknown_delivery_site = child_node.data.unknown_delivery_site

        parent_node.propagate()
        self.assertEqual(child_node.data.transport_document_reference, "ABCD")
        self.assertEqual(child_node.data.unknown_delivery_site, original_child_unknown_delivery_site)
        self.assertEqual(child_node.data.esca, 2.0)

    def test_traceability_lot_to_stock_lot(self):
        parent_lot = CarbureLotFactory.create(added_by=self.entity, carbure_client=self.entity)
        parent_stock = CarbureStockFactory.create(parent_lot=parent_lot, carbure_client=self.entity)
        CarbureLotFactory.create(parent_stock=parent_stock, added_by=self.entity)

        root_node = LotNode(parent_lot)
        stock_node = root_node.get_first(StockNode)
        lot_node = stock_node.get_first(LotNode)

        self.assertEqual(root_node.get_depth(), 0)
        self.assertEqual(stock_node.get_depth(), 1)
        self.assertEqual(lot_node.get_depth(), 2)

        self.assertEqual(len(root_node.children), 1)
        self.assertEqual(root_node.parent, None)
        self.assertEqual(len(stock_node.children), 1)
        self.assertEqual(stock_node.parent, root_node)
        self.assertEqual(lot_node.parent, stock_node)

        root_node.update({"transport_document_reference": "ABCD", "biofuel_id": 12, "unknown_delivery_site": "UNKNOWN", "esca": 2.0})  # fmt:skip
        self.assertEqual(root_node.data.transport_document_reference, "ABCD")
        self.assertEqual(root_node.data.biofuel_id, 12)
        self.assertEqual(root_node.data.unknown_delivery_site, "UNKNOWN")
        self.assertEqual(root_node.data.esca, 2.0)

        original_child_lot_transport_document_reference = lot_node.data.transport_document_reference
        original_child_lot_unknown_delivery_site = lot_node.data.unknown_delivery_site

        root_node.propagate()

        self.assertEqual(stock_node.data.biofuel_id, 12)

        self.assertEqual(lot_node.data.transport_document_reference, original_child_lot_transport_document_reference)
        self.assertEqual(lot_node.data.biofuel_id, 12)
        self.assertEqual(lot_node.data.unknown_delivery_site, original_child_lot_unknown_delivery_site)
        self.assertEqual(lot_node.data.esca, 2.0)

    def test_traceability_lot_to_stock_transform_lot(self):
        parent_lot = CarbureLotFactory.create(added_by=self.entity, carbure_client=self.entity)
        source_stock = CarbureStockFactory.create(parent_lot=parent_lot, carbure_client=self.entity)
        dest_stock = CarbureStockFactory.create(biofuel_id=14, carbure_client=self.entity)
        parent_transformation = CarbureStockTransformFactory.create(source_stock=source_stock, dest_stock=dest_stock, entity=self.entity)  # fmt:skip
        dest_stock.parent_transformation = parent_transformation
        dest_stock.save()
        CarbureLotFactory.create(parent_stock=dest_stock, biofuel_id=14, added_by=self.entity)

        root_node = LotNode(parent_lot)
        source_stock_node = root_node.get_first(StockNode)
        stock_transform_node = source_stock_node.get_first(StockTransformNode)
        dest_stock_node = stock_transform_node.get_first(StockNode)
        lot_node = dest_stock_node.get_first(LotNode)

        self.assertEqual(root_node.get_depth(), 0)
        self.assertEqual(source_stock_node.get_depth(), 1)
        self.assertEqual(stock_transform_node.get_depth(), 2)
        self.assertEqual(dest_stock_node.get_depth(), 3)
        self.assertEqual(lot_node.get_depth(), 4)

        root_node.update({"transport_document_reference": "ABCD", "biofuel_id": 12, "carbure_delivery_site_id": 13, "esca": 2.0})  # fmt:skip
        self.assertEqual(root_node.data.transport_document_reference, "ABCD")
        self.assertEqual(root_node.data.biofuel_id, 12)
        self.assertEqual(root_node.data.carbure_delivery_site_id, 13)
        self.assertEqual(root_node.data.esca, 2.0)

        original_child_lot_transport_document_reference = lot_node.data.transport_document_reference
        original_child_lot_carbure_delivery_site_id = lot_node.data.carbure_delivery_site_id

        root_node.propagate()

        self.assertEqual(source_stock_node.data.depot_id, 13)
        self.assertEqual(source_stock_node.data.biofuel_id, 12)

        self.assertEqual(dest_stock_node.data.depot_id, 13)
        self.assertEqual(dest_stock_node.data.biofuel_id, 14)

        self.assertEqual(lot_node.data.transport_document_reference, original_child_lot_transport_document_reference)
        self.assertEqual(lot_node.data.biofuel_id, 14)
        self.assertEqual(lot_node.data.carbure_delivery_site_id, original_child_lot_carbure_delivery_site_id)
        self.assertEqual(lot_node.data.esca, 2.0)

    def test_traceability_lot_to_ticket_source(self):
        parent_lot = CarbureLotFactory.create(added_by=self.entity)
        SafTicketSourceFactory.create(parent_lot=parent_lot, added_by=self.entity)

        parent_node = LotNode(parent_lot)
        ticket_source_node = parent_node.get_first(TicketSourceNode)

        parent_node.update({"biofuel_id": 12, "volume": 123456, "unknown_production_site": "UNKNOWN", "esca": 2.0})  # fmt:skip
        self.assertEqual(parent_node.data.biofuel_id, 12)
        self.assertEqual(parent_node.data.volume, 123456)
        self.assertEqual(parent_node.data.unknown_production_site, "UNKNOWN")
        self.assertEqual(parent_node.data.esca, 2.0)

        parent_node.propagate()

        self.assertEqual(ticket_source_node.data.biofuel_id, 12)
        self.assertEqual(ticket_source_node.data.total_volume, 123456)
        self.assertEqual(ticket_source_node.data.unknown_production_site, "UNKNOWN")
        self.assertEqual(ticket_source_node.data.esca, 2.0)

    def test_traceability_lot_to_ticket(self):
        parent_lot = CarbureLotFactory.create(added_by=self.entity)
        parent_ticket_source = SafTicketSourceFactory.create(parent_lot=parent_lot, added_by=self.entity)
        SafTicketFactory.create(parent_ticket_source=parent_ticket_source, supplier=self.entity)

        parent_node = LotNode(parent_lot)
        ticket_node = parent_node.get_first(TicketNode)

        parent_node.update({"biofuel_id": 12, "volume": 123456, "unknown_production_site": "UNKNOWN", "esca": 2.0})  # fmt:skip
        self.assertEqual(parent_node.data.biofuel_id, 12)
        self.assertEqual(parent_node.data.volume, 123456)
        self.assertEqual(parent_node.data.unknown_production_site, "UNKNOWN")
        self.assertEqual(parent_node.data.esca, 2.0)

        parent_node.propagate()

        self.assertEqual(ticket_node.data.biofuel_id, 12)
        self.assertEqual(ticket_node.data.unknown_production_site, "UNKNOWN")
        self.assertEqual(ticket_node.data.esca, 2.0)

    def test_traceability_lot_to_parent_lot(self):
        parent_lot = CarbureLotFactory.create(added_by=self.entity)
        child_lot = CarbureLotFactory.create(parent_lot=parent_lot, added_by=self.entity)

        child_node = LotNode(child_lot)
        parent_node = child_node.parent

        self.assertEqual(parent_node.get_depth(), 0)
        self.assertEqual(child_node.get_depth(), 1)

        child_node.update({"transport_document_reference": "ABCD", "unknown_delivery_site": "UNKNOWN", "esca": 2.0})
        self.assertEqual(child_node.data.transport_document_reference, "ABCD")
        self.assertEqual(child_node.data.unknown_delivery_site, "UNKNOWN")
        self.assertEqual(child_node.data.esca, 2.0)

        original_parent_unknown_delivery_site = parent_node.data.unknown_delivery_site

        child_node.propagate()

        self.assertEqual(parent_node.data.transport_document_reference, "ABCD")
        self.assertEqual(parent_node.data.unknown_delivery_site, original_parent_unknown_delivery_site)
        self.assertEqual(parent_node.data.esca, 2.0)

    def test_traceability_stock_to_parent_lot(self):
        parent_lot = CarbureLotFactory.create(added_by=self.entity, carbure_client=self.entity)
        child_stock = CarbureStockFactory.create(parent_lot=parent_lot, carbure_client=self.entity)
        child_lot = CarbureLotFactory.create(parent_stock=child_stock, added_by=self.entity)

        child_node = LotNode(child_lot)
        stock_node = child_node.parent
        root_node = child_node.get_root()

        self.assertEqual(root_node.get_depth(), 0)
        self.assertEqual(child_node.get_depth(), 2)

        child_node.update({"transport_document_reference": "ABCD", "biofuel_id": 12, "carbure_delivery_site_id": 13, "esca": 2.0})  # fmt:skip
        self.assertEqual(child_node.data.transport_document_reference, "ABCD")
        self.assertEqual(child_node.data.biofuel_id, 12)
        self.assertEqual(child_node.data.carbure_delivery_site_id, 13)
        self.assertEqual(child_node.data.esca, 2.0)

        original_parent_dae = root_node.data.transport_document_reference
        original_parent_carbure_delivery_site_id = root_node.data.carbure_delivery_site_id

        child_node.propagate()

        self.assertEqual(stock_node.data.biofuel_id, 12)

        self.assertEqual(root_node.data.biofuel_id, 12)
        self.assertEqual(root_node.data.transport_document_reference, original_parent_dae)
        self.assertEqual(root_node.data.carbure_delivery_site_id, original_parent_carbure_delivery_site_id)
        self.assertEqual(root_node.data.esca, 2.0)

    def test_traceability_stock_volume_check(self):
        # @TODO check that a stock with not enough volume throws an error
        pass

    def test_traceability_ticket_source_volume_check(self):
        # @TODO check that a stock with not enough volume throws an error
        pass

    def test_traceability_different_owners(self):
        # @TODO check how data is propagated between nodes of different owners
        pass
