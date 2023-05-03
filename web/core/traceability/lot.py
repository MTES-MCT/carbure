from core.common import compute_quantities
from core.models import CarbureLot
from .node import Node, GHG_FIELDS


class LotNode(Node):
    type = Node.LOT

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
        "carbure_supplier",
        "unknown_supplier",
        "supplier",
        "supplier_certificate",
        "supplier_certificate_type",
        "vendor_certificate",
        "vendor_certificate_type",
        "carbure_client_id",
        "carbure_client",
        "unknown_client",
        "client",
        "delivery_type",
        "free_field",
    ]

    TRANSPORT_FIELDS = [
        "transport_document_reference",
        "transport_document_type",
        "volume",
        "weight",
        "lhv_amount",
    ]

    DELIVERY_FIELDS = [
        "year",
        "period",
        "delivery_date",
        "delivery_site",
        "carbure_delivery_site",
        "carbure_delivery_site_id",
        "unknown_delivery_site",
        "delivery_site_country",
    ]

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
        allowed_fields = ["production_site_certificate_type"]

        root_lot = self.get_root()
        has_no_ancestor_stock = self.get_closest(Node.STOCK) is None
        owns_ancestor_stock = self.get_closest(Node.STOCK, owner=entity_id) is not None

        if self.owner == entity_id:
            allowed_fields += LotNode.TRANSACTION_FIELDS
            if has_no_ancestor_stock or owns_ancestor_stock:
                allowed_fields += LotNode.DELIVERY_FIELDS

            closest_lot = self.get_closest(Node.LOT, owner=entity_id)
            owns_ancestor_lot = closest_lot is not None and (closest_lot.parent is None or closest_lot.parent.owner == entity_id)  # fmt:skip
            if self.parent is None or owns_ancestor_lot or owns_ancestor_stock:
                allowed_fields += LotNode.TRANSPORT_FIELDS

        if root_lot.owner == entity_id:
            allowed_fields += LotNode.SUSTAINABILITY_FIELDS

        return allowed_fields

    def get_disabled_fields(self, entity_id) -> list[str]:
        all_fields = (
            LotNode.TRANSACTION_FIELDS
            + LotNode.DELIVERY_FIELDS
            + LotNode.TRANSPORT_FIELDS
            + LotNode.SUSTAINABILITY_FIELDS
        )

        allowed_fields = self.get_allowed_fields(entity_id)
        return list(set(all_fields) - set(allowed_fields))

    def diff_with_parent(self):
        if self.parent.type == Node.LOT:
            return self.get_diff(LotNode.FROM_PARENT_LOT, self.parent)
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
            return self.get_diff(LotNode.FROM_CHILD_LOT, child)
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
