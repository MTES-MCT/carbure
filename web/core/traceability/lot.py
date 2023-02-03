from core.models import CarbureLot
from .node import Node, GHG_FIELDS


class LotNode(Node):
    FROM_LOT = {
        "country_of_origin_id": True,
        "carbure_producer_id": True,
        "unknown_producer": True,
        "carbure_production_site_id": True,
        "unknown_production_site": True,
        "production_country_id": True,
        "production_site_commissioning_date": True,
        "production_site_certificate": True,
        "production_site_double_counting_certificate": True,
        "delivery_date": True,
        "ghg_total": True,
        "ghg_reference": True,
        "ghg_reduction": True,
        "ghg_reference_red_ii": True,
        "ghg_reduction_red_ii": True,
        **GHG_FIELDS,
    }

    FROM_DIRECT_LOT = {
        "feedstock_id": True,
        "biofuel_id": True,
        "volume": True,
        "weight": True,
        "lhv_amount": True,
        "transport_document_type": True,
        "transport_document_reference": True,
        "carbure_delivery_site_id": True,
        "unknown_delivery_site": True,
        "delivery_site_country_id": True,
        **FROM_LOT,
    }

    FROM_PARENT_LOT = {
        "carbure_client_id": "carbure_supplier_id",
        **FROM_DIRECT_LOT,
    }

    FROM_CHILD_LOT = {
        "carbure_supplier_id": "carbure_client_id",
        **FROM_DIRECT_LOT,
    }

    FROM_STOCK = {
        "biofuel_id": True,
        "feedstock_id": True,
        "country_of_origin_id": True,
        "carbure_production_site_id": True,
        "unknown_production_site": True,
        "production_country_id": True,
        "ghg_reduction": True,
        "ghg_reduction_red_ii": True,
    }

    FROM_PARENT_STOCK = {
        "carbure_client_id": "carbure_supplier_id",
        **FROM_STOCK,
    }

    FROM_CHILD_STOCK = {
        "carbure_supplier_id": True,
        "unknown_supplier": True,
        "carbure_client_id": True,
        "depot_id": "carbure_delivery_site_id",
        **FROM_STOCK,
    }

    TRANSACTION_FIELDS = [
        "carbure_supplier_id",
        "unknown_supplier",
        "supplier_certificate",
        "carbure_client_id",
        "unknown_client",
        "delivery_type",
    ]

    DELIVERY_FIELDS = [
        "transport_document_reference",
        "transport_document_type",
        "volume",
        "weight",
        "lhv_amount",
        "delivery_date",
        "carbure_delivery_site_id",
        "unknown_delivery_site",
        "delivery_site_country",
    ]

    SUSTAINABILITY_FIELDS = [
        "feedstock",
        "biofuel",
        "country_of_origin",
        "carbure_producer",
        "unknown_producer",
        "carbure_production_site",
        "unknown_production_site",
        "production_country",
        "production_site_commissioning_date",
        "production_site_certificate",
        "production_site_double_counting_certificate",
        "eec",
        "el",
        "ep",
        "etd",
        "eu",
        "esca",
        "eccs",
        "eccr",
        "eee",
        "ghg_total",
        "ghg_reference",
        "ghg_reduction",
        "ghg_reference_red_ii",
        "ghg_reduction_red_ii",
    ]

    def serialize(self):
        return {
            "type": "LOT",
            "id": self.data.id,
            "carbure_id": self.data.carbure_id,
            "biofuel": self.data.biofuel.name,
            "volume": self.data.volume,
            "period": self.data.period,
        }

    def get_owner(self):
        return self.data.added_by_id

    def get_parent(self):
        from .stock import StockNode

        if self.data.parent_lot:
            return LotNode(self.data.parent_lot, child=self)
        if self.data.parent_stock:
            return StockNode(self.data.parent_stock, child=self)

    def get_children(self):
        from .stock import StockNode
        from .ticket_source import TicketSourceNode

        children_lot = [LotNode(lot, parent=self) for lot in self.data.carburelot_set.exclude(lot_status=CarbureLot.DELETED)]  # fmt:skip
        children_stock = [StockNode(stock, parent=self) for stock in self.data.carburestock_set.all()]
        children_ticket_source = [TicketSourceNode(ticket_source, parent=self) for ticket_source in self.data.safticketsource_set.all()]  # fmt:skip
        return children_lot + children_stock + children_ticket_source

    def get_allowed_fields(self, entity_id) -> list:
        from .stock import StockNode

        allowed_fields = []

        root_lot = self.get_root()
        has_no_ancestor_stock = self.get_closest(StockNode) is None
        owns_ancestor_stock = self.get_closest(StockNode, owner=entity_id) is not None

        if self.owner == entity_id:
            allowed_fields += LotNode.TRANSACTION_FIELDS
        if has_no_ancestor_stock or owns_ancestor_stock:
            allowed_fields += LotNode.DELIVERY_FIELDS
        if root_lot.owner == entity_id:
            allowed_fields += LotNode.SUSTAINABILITY_FIELDS

        return allowed_fields

    def diff_with_parent(self):
        from .stock import StockNode

        if isinstance(self.parent, LotNode):
            return self.get_diff(LotNode.FROM_PARENT_LOT, self.parent)
        if isinstance(self.parent, StockNode):
            # get diff with root lot sustainability data
            ancestor_lot = self.parent.get_closest(LotNode)
            lot_diff = self.get_diff(LotNode.FROM_LOT, ancestor_lot)
            # get diff with stock info
            stock_diff = self.get_diff(LotNode.FROM_PARENT_STOCK, self.parent)
            # merge the results
            return {**lot_diff, **stock_diff}

        return {}

    def diff_with_child(self, child: Node):
        from .stock import StockNode

        # we ignore ticket source children because they cannot be modified directly anyway
        if isinstance(child, LotNode):
            return self.get_diff(LotNode.FROM_CHILD_LOT, child)
        if isinstance(child, StockNode):
            # get first descendant lot for sustainability data
            descendant_lot = child.get_first(LotNode)
            descendant_diff = self.get_diff(LotNode.FROM_LOT, descendant_lot)
            # get diff with stock info
            stock_diff = self.get_diff(LotNode.FROM_CHILD_STOCK, child)
            # merge the results
            return {**descendant_diff, **stock_diff}
        return {}
