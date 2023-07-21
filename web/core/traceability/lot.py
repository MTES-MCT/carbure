from core.common import compute_quantities
from core.models import CarbureLot
from .node import Node, GHG_FIELDS


class LotNode(Node):
    type = Node.LOT

    # data to copy from a related lot
    FROM_LOT = {
        "country_of_origin": True,
        "carbure_producer": True,
        "unknown_producer": True,
        "carbure_production_site": True,
        "unknown_production_site": True,
        "production_country": True,
        "production_site_commissioning_date": True,
        "production_site_certificate": True,
        "production_site_certificate_type": True,
        "production_site_double_counting_certificate": True,
        "ghg_total": True,
        "ghg_reference": True,
        "ghg_reduction": True,
        "ghg_reference_red_ii": True,
        "ghg_reduction_red_ii": True,
        **GHG_FIELDS,
    }

    # data to copy from a directly related lot
    FROM_DIRECT_LOT = {
        "feedstock": True,
        "biofuel": True,
        "volume": True,
        "weight": True,
        "lhv_amount": True,
        "transport_document_type": True,
        "transport_document_reference": True,
        "carbure_delivery_site": True,
        "unknown_delivery_site": True,
        "delivery_site_country": True,
        **FROM_LOT,
    }

    # data to copy only from a related processing lot
    FROM_PROCESSING_LOT = {
        "supplier_certificate": True,
    }

    # data to copy only from a direct parent lot
    FROM_PARENT_LOT = {
        "carbure_client": "carbure_supplier",
        **FROM_DIRECT_LOT,
    }

    # data to copy only from a direct child lot
    FROM_CHILD_LOT = {
        "carbure_supplier": "carbure_client",
        **FROM_DIRECT_LOT,
    }

    # data to copy only from a related stock
    FROM_STOCK = {
        "biofuel": True,
        "feedstock": True,
        "country_of_origin": True,
        "carbure_production_site": True,
        "unknown_production_site": True,
        "production_country": True,
        "ghg_reduction": True,
        "ghg_reduction_red_ii": True,
    }

    # data to copy only from a direct parent stock
    FROM_PARENT_STOCK = {
        "carbure_client": "carbure_supplier",
        **FROM_STOCK,
    }

    # data to copy only from a direct child stock
    FROM_CHILD_STOCK = {
        "carbure_supplier": True,
        "unknown_supplier": True,
        "carbure_client": True,
        "depot": "carbure_delivery_site",
        **FROM_STOCK,
    }

    # fields that are always allowed for a lot owner (the one who added the lot, either from drafts or trading or processing)
    TRANSACTION_FIELDS = [
        "carbure_supplier_id",
        "carbure_supplier",
        "unknown_supplier",
        "supplier",
        "vendor_certificate",
        "vendor_certificate_type",
        "carbure_client_id",
        "carbure_client",
        "unknown_client",
        "client",
        "delivery_type",
        "free_field",
    ]

    # fields only available for lots created after trading (with or without stock)
    TRADING_FIELDS = [
        "supplier_certificate",
        "supplier_certificate_type",
        "year",
        "period",
        "delivery_date",
    ]

    # fields only available for stock extracts
    DELIVERY_FIELDS = [
        "transport_document_reference",
        "transport_document_type",
        "volume",
        "weight",
        "lhv_amount",
        "delivery_site",
        "carbure_delivery_site",
        "carbure_delivery_site_id",
        "unknown_delivery_site",
        "delivery_site_country",
    ]

    # fields only available to the root owner (the one who input the data first on carbure)
    SUSTAINABILITY_FIELDS = [
        "feedstock",
        "feedstock_id",
        "biofuel",
        "biofuel_id",
        "country_of_origin",
        "country_of_origin_id",
        "producer",
        "carbure_producer",
        "carbure_producer_id",
        "unknown_producer",
        "production_site",
        "carbure_production_site",
        "carbure_production_site_id",
        "unknown_production_site",
        "production_country",
        "production_country_id",
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

    def get_data(self):
        return {
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
        # only allow owner to update a lot directly
        if self.owner != entity_id:
            return []

        # if the lot has no parent, allow all fields
        if self.parent is None:
            return LotNode.TRANSACTION_FIELDS + LotNode.TRADING_FIELDS + LotNode.DELIVERY_FIELDS + LotNode.SUSTAINABILITY_FIELDS  # fmt:skip

        # find the first lot of the current traceability chain
        sustainability_root = self.get_root()

        # find the closest node in which delivery fields were defined (= closest lot with a parent stock, or the global root)
        delivery_root = self.get_closest(is_delivery_root)

        # find out if the current lot came from trading another lot
        is_parent_trading = self.parent.type == Node.LOT and self.parent.data.delivery_type == CarbureLot.TRADING

        # by default, the owner can change all transaction fields
        allowed_fields = [*LotNode.TRANSACTION_FIELDS]

        # if the entity also owns the root lot of this chain, allow sustainability fields
        if sustainability_root.owner == entity_id:
            allowed_fields += LotNode.SUSTAINABILITY_FIELDS

        # if the lot came from a stock owned by the current entity, allow delivery and trading fields
        if delivery_root.owner == entity_id:
            allowed_fields += LotNode.DELIVERY_FIELDS + LotNode.TRADING_FIELDS
        # otherwise if the lot comes from trading, allow trading fields
        elif is_parent_trading:
            allowed_fields += LotNode.TRADING_FIELDS

        return allowed_fields

    def get_disabled_fields(self, entity_id) -> tuple[bool, list[str]]:
        all_fields = LotNode.TRANSACTION_FIELDS + LotNode.TRADING_FIELDS + LotNode.DELIVERY_FIELDS + LotNode.SUSTAINABILITY_FIELDS  # fmt:skip

        allowed_fields = self.get_allowed_fields(entity_id)
        disabled_fields = list(set(all_fields) - set(allowed_fields))

        is_read_only = len(allowed_fields) == 0
        return is_read_only, disabled_fields

    def diff_with_parent(self):
        if self.parent.type == Node.LOT:
            mapping = LotNode.FROM_PARENT_LOT
            if self.parent.data.delivery_type == CarbureLot.PROCESSING:
                mapping = {**mapping, **LotNode.FROM_PROCESSING_LOT}
            return self.get_diff(mapping, self.parent)
        if self.parent.type == Node.STOCK:
            # get diff with root lot sustainability data
            ancestor_lot = self.parent.get_closest(Node.LOT)
            lot_diff = self.get_diff(LotNode.FROM_LOT, ancestor_lot)
            # get diff with stock info
            stock_diff = self.get_diff(LotNode.FROM_PARENT_STOCK, self.parent)
            # merge the results
            return {**lot_diff, **stock_diff}

        return {}

    def diff_with_child(self, child: Node):
        # we ignore ticket source children because they cannot be modified directly anyway
        if child.type == Node.LOT:
            mapping = LotNode.FROM_CHILD_LOT
            if self.data.delivery_type == CarbureLot.PROCESSING:
                mapping = {**mapping, **LotNode.FROM_PROCESSING_LOT}
            return self.get_diff(mapping, child)
        if child.type == Node.STOCK:
            # get first descendant lot for sustainability data
            descendant_lot = child.get_first(Node.LOT)
            descendant_diff = self.get_diff(LotNode.FROM_LOT, descendant_lot)
            # get diff with stock info
            stock_diff = self.get_diff(LotNode.FROM_CHILD_STOCK, child)
            # merge the results
            return {**descendant_diff, **stock_diff}
        return {}

    def remove_from_tree(self):
        # if the parent is a CarbureLot, put it back into PENDING mode
        if self.parent and self.parent.type == Node.LOT:
            self.parent.update({"lot_status": CarbureLot.PENDING, "delivery_type": CarbureLot.UNKNOWN})
            return [self.parent]

        # if the parent is a CarbureStock, credit back the extracted volume
        if self.parent and self.parent.type == Node.STOCK:
            biofuel = self.parent.data.biofuel
            remaining_volume = self.parent.data.remaining_volume + self.data.volume
            volume, weight, lhv_amount = compute_quantities(biofuel, volume=remaining_volume)
            self.parent.update({"remaining_volume": volume, "remaining_weight": weight, "remaining_lhv_amount": lhv_amount})  # fmt:skip
            return [self.parent]

        return []

    def derive_fields(self, update):
        derived_fields = {}
        for field, value in update.items():
            if field == "delivery_date":
                derived_fields["year"] = value.year
                derived_fields["period"] = value.year * 100 + value.month
            if field == "carbure_production_site" and value:
                derived_fields["production_country"] = value.country
                derived_fields["production_site_commissioning_date"] = value.date_mise_en_service
            if field == "carbure_delivery_site" and value:
                derived_fields["delivery_site_country"] = value.country
        return derived_fields


# function to check if a given node can be considered a root for DELIVERY_FIELDS data
# looks up for the first lot in the chain that comes from a stock
# otherwise, accepts the root node of the chain
def is_delivery_root(node: Node):
    if node.parent is None:
        return True

    is_lot = node.type == Node.LOT
    has_parent_stock = node.parent.type == Node.STOCK

    return is_lot and has_parent_stock
