from django.test import TestCase

from core.models import (
    Biocarburant,
    CarbureLot,
    CarbureStock,
    CarbureStockTransformation,
    Entity,
)
from core.tests_utils import setup_current_user
from core.traceability import LotNode, Node
from saf.factories import SafTicketFactory, SafTicketSourceFactory
from saf.models import SafTicket, SafTicketSource
from transactions.factories import (
    CarbureLotFactory,
    CarbureStockFactory,
    CarbureStockTransformFactory,
)


class TraceabilityTest(TestCase):
    fixtures = [
        "json/biofuels.json",
        "json/feedstock.json",
        "json/countries.json",
        "json/entities.json",
        "json/productionsites.json",
        "json/depots.json",
        "json/entities_sites.json",
    ]

    def setUp(self):
        self.eth = Biocarburant.objects.get(code="ETH").id
        self.etbe = Biocarburant.objects.get(code="ETBE").id

        entities = Entity.objects.filter(entity_type=Entity.OPERATOR)
        self.entity = entities[0]
        self.entity2 = entities[1]
        self.user = setup_current_user(self, "tester@carbure.local", "Tester", "gogogo", [(self.entity, "ADMIN")])

        CarbureLot.objects.all().delete()
        CarbureStock.objects.all().delete()
        CarbureStockTransformation.objects.all().delete()
        SafTicketSource.objects.all().delete()
        SafTicket.objects.all().delete()

    def test_traceability_single_lot(self):
        lot = CarbureLotFactory.create(lot_status="ACCEPTED")
        node = LotNode(lot)

        assert node.get_depth() == 0
        assert len(node.children) == 0

        node.update({"carbure_id": "ABCD"})
        assert lot.carbure_id == "ABCD"

    def test_traceability_lot_to_lot(self):
        parent_lot = CarbureLotFactory.create(
            lot_status="ACCEPTED",
            added_by=self.entity,
            delivery_type=CarbureLot.TRADING,
            supplier_certificate="PARENT_CERT",
            parent_lot=None,
        )

        CarbureLotFactory.create(
            lot_status="ACCEPTED",
            parent_lot=parent_lot,
            added_by=self.entity,
            delivery_type=CarbureLot.BLENDING,
            supplier_certificate="CHILD_CERT",
        )

        parent_node = LotNode(parent_lot)
        child_node = parent_node.get_first(Node.LOT)

        original_child_supplier_cert = child_node.data.supplier_certificate

        assert parent_node.get_depth() == 0
        assert child_node.get_depth() == 1

        assert len(parent_node.children) == 1
        assert child_node.parent == parent_node
        assert parent_node.children[0] == child_node

        parent_node.update(
            {
                "transport_document_reference": "ABCD",
                "supplier_certificate": "CERT",
                "esca": 2.0,
            }
        )

        assert parent_node.data.transport_document_reference == "ABCD"
        assert parent_node.data.supplier_certificate == "CERT"
        assert parent_node.data.esca == 2.0

        parent_node.propagate()

        assert child_node.data.transport_document_reference == "ABCD"
        assert child_node.data.supplier_certificate == original_child_supplier_cert
        assert child_node.data.esca == 2.0

    def test_traceability_lot_to_stock_lot(self):
        parent_lot = CarbureLotFactory.create(lot_status="ACCEPTED", added_by=self.entity, carbure_client=self.entity)
        parent_stock = CarbureStockFactory.create(parent_lot=parent_lot, carbure_client=self.entity)
        CarbureLotFactory.create(lot_status="ACCEPTED", parent_stock=parent_stock, added_by=self.entity)

        root_node = LotNode(parent_lot)
        stock_node = root_node.get_first(Node.STOCK)
        lot_node = stock_node.get_first(Node.LOT)

        assert root_node.get_depth() == 0
        assert stock_node.get_depth() == 1
        assert lot_node.get_depth() == 2

        assert len(root_node.children) == 1
        assert root_node.parent is None
        assert len(stock_node.children) == 1
        assert stock_node.parent == root_node
        assert lot_node.parent == stock_node

        root_node.update(
            {"transport_document_reference": "ABCD", "biofuel_id": 12, "unknown_delivery_site": "UNKNOWN", "esca": 2.0}
        )
        assert root_node.data.transport_document_reference == "ABCD"
        assert root_node.data.biofuel_id == 12
        assert root_node.data.unknown_delivery_site == "UNKNOWN"
        assert root_node.data.esca == 2.0

        original_child_lot_transport_document_reference = lot_node.data.transport_document_reference
        original_child_lot_unknown_delivery_site = lot_node.data.unknown_delivery_site

        root_node.propagate()

        assert stock_node.data.biofuel_id == 12

        assert lot_node.data.transport_document_reference == original_child_lot_transport_document_reference
        assert lot_node.data.biofuel_id == 12
        assert lot_node.data.unknown_delivery_site == original_child_lot_unknown_delivery_site
        assert lot_node.data.esca == 2.0

    def test_traceability_lot_to_stock_transform_lot(self):
        root_lot = CarbureLotFactory.create(
            lot_status="ACCEPTED",
            added_by=self.entity,
            carbure_client=self.entity,
            biofuel_id=self.eth,
        )
        source_stock = CarbureStockFactory.create(parent_lot=root_lot, carbure_client=self.entity)
        dest_stock = CarbureStockFactory.create(carbure_client=self.entity)
        parent_transformation = CarbureStockTransformFactory.create(
            source_stock=source_stock, dest_stock=dest_stock, entity=self.entity
        )
        dest_stock.parent_transformation = parent_transformation
        dest_stock.save()
        CarbureLotFactory.create(lot_status="ACCEPTED", parent_stock=dest_stock, added_by=self.entity)

        root_node = LotNode(root_lot)
        source_stock_node = root_node.get_first(Node.STOCK)
        stock_transform_node = source_stock_node.get_first(Node.STOCK_TRANSFORM)
        dest_stock_node = stock_transform_node.get_first(Node.STOCK)
        child_node = dest_stock_node.get_first(Node.LOT)

        assert root_node.get_depth() == 0
        assert source_stock_node.get_depth() == 1
        assert stock_transform_node.get_depth() == 2
        assert dest_stock_node.get_depth() == 3
        assert child_node.get_depth() == 4

        root_node.update({"transport_document_reference": "ABCD", "carbure_delivery_site_id": 13, "esca": 2.0})
        assert root_node.data.transport_document_reference == "ABCD"
        assert root_node.data.biofuel_id == self.eth
        assert root_node.data.carbure_delivery_site_id == 13
        assert root_node.data.esca == 2.0

        original_child_lot_transport_document_reference = child_node.data.transport_document_reference
        original_child_lot_carbure_delivery_site_id = child_node.data.carbure_delivery_site_id

        root_node.propagate()

        assert source_stock_node.data.depot_id == 13
        assert source_stock_node.data.biofuel_id == self.eth

        assert dest_stock_node.data.carbure_supplier_id == self.entity.id
        assert dest_stock_node.data.depot_id == 13
        assert dest_stock_node.data.biofuel_id == self.etbe

        assert child_node.data.transport_document_reference == original_child_lot_transport_document_reference
        assert child_node.data.biofuel_id == self.etbe
        assert child_node.data.carbure_delivery_site_id == original_child_lot_carbure_delivery_site_id
        assert child_node.data.esca == 2.0

    def test_traceability_lot_to_ticket_source(self):
        parent_lot = CarbureLotFactory.create(lot_status="ACCEPTED", added_by=self.entity)
        SafTicketSourceFactory.create(parent_lot=parent_lot, added_by=self.entity)

        parent_node = LotNode(parent_lot)
        ticket_source_node = parent_node.get_first(Node.TICKET_SOURCE)

        parent_node.update({"biofuel_id": 12, "volume": 123456, "unknown_production_site": "UNKNOWN", "esca": 2.0})
        assert parent_node.data.biofuel_id == 12
        assert parent_node.data.volume == 123456
        assert parent_node.data.unknown_production_site == "UNKNOWN"
        assert parent_node.data.esca == 2.0

        parent_node.propagate()

        assert ticket_source_node.data.biofuel_id == 12
        assert ticket_source_node.data.total_volume == 123456
        assert ticket_source_node.data.unknown_production_site == "UNKNOWN"
        assert ticket_source_node.data.esca == 2.0

    def test_traceability_lot_to_ticket(self):
        parent_lot = CarbureLotFactory.create(lot_status="ACCEPTED", added_by=self.entity)
        parent_ticket_source = SafTicketSourceFactory.create(parent_lot=parent_lot, added_by=self.entity)
        SafTicketFactory.create(parent_ticket_source=parent_ticket_source, supplier=self.entity)

        parent_node = LotNode(parent_lot)
        ticket_node = parent_node.get_first(Node.TICKET)

        parent_node.update({"biofuel_id": 12, "volume": 123456, "unknown_production_site": "UNKNOWN", "esca": 2.0})
        assert parent_node.data.biofuel_id == 12
        assert parent_node.data.volume == 123456
        assert parent_node.data.unknown_production_site == "UNKNOWN"
        assert parent_node.data.esca == 2.0

        parent_node.propagate()

        assert ticket_node.data.biofuel_id == 12
        assert ticket_node.data.unknown_production_site == "UNKNOWN"
        assert ticket_node.data.esca == 2.0

    def test_traceability_lot_to_parent_lot(self):
        parent_lot = CarbureLotFactory.create(lot_status="ACCEPTED", added_by=self.entity, delivery_type=CarbureLot.TRADING)
        child_lot = CarbureLotFactory.create(lot_status="ACCEPTED", parent_lot=parent_lot, added_by=self.entity)

        child_node = LotNode(child_lot)
        parent_node = child_node.parent

        assert parent_node.get_depth() == 0
        assert child_node.get_depth() == 1

        child_node.update(
            {
                "transport_document_reference": "ABCD",
                "supplier_certificate": "CERT",
                "esca": 2.0,
            }
        )
        assert child_node.data.transport_document_reference == "ABCD"
        assert child_node.data.supplier_certificate == "CERT"
        assert child_node.data.esca == 2.0

        original_parent_supplier_cert = parent_node.data.supplier_certificate

        child_node.propagate()

        assert parent_node.data.transport_document_reference == "ABCD"
        assert parent_node.data.supplier_certificate == original_parent_supplier_cert
        assert parent_node.data.esca == 2.0

    def test_traceability_stock_to_parent_lot(self):
        root_lot = CarbureLotFactory.create(
            lot_status="ACCEPTED", added_by=self.entity, carbure_client=self.entity, carbure_delivery_site_id=91
        )
        child_stock = CarbureStockFactory.create(parent_lot=root_lot, carbure_client=self.entity, depot_id=10)
        child_lot = CarbureLotFactory.create(lot_status="ACCEPTED", parent_stock=child_stock, added_by=self.entity)

        child_node = LotNode(child_lot)
        stock_node = child_node.parent
        root_node = child_node.get_root()

        assert root_node.get_depth() == 0
        assert child_node.get_depth() == 2

        child_node.update(
            {"transport_document_reference": "ABCD", "biofuel_id": 12, "carbure_delivery_site_id": 13, "esca": 2.0}
        )
        assert child_node.data.transport_document_reference == "ABCD"
        assert child_node.data.biofuel_id == 12
        assert child_node.data.carbure_delivery_site_id == 13
        assert child_node.data.esca == 2.0

        original_parent_dae = root_node.data.transport_document_reference
        original_parent_depot_id = stock_node.data.depot_id

        child_node.propagate()

        assert stock_node.data.biofuel_id == 12
        assert stock_node.data.depot_id == original_parent_depot_id

        assert root_node.data.biofuel_id == 12
        assert root_node.data.transport_document_reference == original_parent_dae
        assert root_node.data.carbure_delivery_site_id == original_parent_depot_id
        assert root_node.data.esca == 2.0

    def test_traceability_different_owners(self):
        parent_lot = CarbureLotFactory.create(
            lot_status="ACCEPTED",
            added_by=self.entity,
            esca=3,
        )

        CarbureLotFactory.create(
            lot_status="ACCEPTED",
            parent_lot=parent_lot,
            added_by=self.entity2,
            unknown_client="SOMEBODY",
            esca=10,
        )

        parent_node = LotNode(parent_lot)
        child_node = parent_node.children[0]

        # try to update the parent as entity1
        expected_diff = {"esca": (2, 3)}
        result = parent_node.update({"esca": 2}, self.entity.id)
        assert result == expected_diff

        parent_node.propagate()
        assert parent_node.data.esca == 2
        assert child_node.data.esca == 2

        # try to update the parent as entity2
        try:
            parent_node.update({"esca": 1}, self.entity2.id)
            raise AssertionError()
        except Exception:
            pass

        # try to update sustainability fields on the child as entity2
        try:
            parent_node.update({"esca": 1}, self.entity2.id)
            raise AssertionError()
        except Exception:
            pass

        # try to update delivery fields on the child as entity2
        expected_diff = ("UNKNOWN", "SOMEBODY")
        result = child_node.update({"unknown_client": "UNKNOWN"}, self.entity2.id)
        assert result["unknown_client"] == expected_diff

    def test_traceability_stock_transform_to_parent_lot(self):
        # @TODO check that the correct values propagate up the chain
        pass

    def test_traceability_stock_volume_check(self):
        # @TODO check that a stock with not enough volume throws an error
        pass

    def test_traceability_ticket_source_volume_check(self):
        # @TODO check that a stock with not enough volume throws an error
        pass
