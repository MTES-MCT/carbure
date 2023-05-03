from core.models import CarbureLot, Biocarburant
from .node import Node, TraceabilityError

ETHANOL = -1
ETBE = -1


def get_stock_transform_biofuels(stock_transform):
    if stock_transform.transformation_type == "ETH_ETBE":
        global ETHANOL, ETBE
        if ETHANOL == -1 or ETBE == -1:
            ETHANOL = Biocarburant.objects.get(code="ETH").id
            ETBE = Biocarburant.objects.get(code="ETBE").id
        return {"source": ETHANOL, "destination": ETBE}
    return {}


class StockNode(Node):
    type = Node.STOCK

    FROM_LOT = {
        "biofuel_id": True,
        "feedstock_id": True,
        "country_of_origin_id": True,
        "carbure_production_site_id": True,
        "unknown_production_site": True,
        "production_country_id": True,
        "ghg_reduction": True,
        "ghg_reduction_red_ii": True,
    }

    FROM_PARENT_LOT = {
        "carbure_delivery_site_id": "depot_id",
        "carbure_supplier_id": True,
        "unknown_supplier": True,
        "carbure_client_id": True,
        **FROM_LOT,
    }

    FROM_CHILD_LOT = {
        "carbure_supplier_id": "carbure_client_id",
        **FROM_LOT,
    }

    FROM_STOCK = {
        "feedstock_id": True,
        "country_of_origin_id": True,
        "depot_id": True,
        "carbure_client_id": True,
        "carbure_production_site_id": True,
        "unknown_production_site": True,
        "production_country_id": True,
        "ghg_reduction": True,
        "ghg_reduction_red_ii": True,
    }

    FROM_PARENT_STOCK_TRANSFORM = {
        "entity_id": "carbure_supplier_id",
    }

    FROM_CHILD_STOCK_TRANSFORM = {
        "entity_id": "carbure_client_id",
    }

    def get_data(self):
        return {
            "carbure_id": self.data.carbure_id,
            "biofuel": self.data.biofuel.name,
            "remaining_volume": self.data.remaining_volume,
        }

    def get_owner(self):
        return self.data.carbure_client_id

    def get_parent(self):
        from .lot import LotNode
        from .stock_transform import StockTransformNode

        if self.data.parent_lot:
            return LotNode(self.data.parent_lot, child=self)
        if self.data.parent_transformation:
            return StockTransformNode(self.data.parent_transformation, child=self)

    def get_children(self):
        from .lot import LotNode
        from .stock_transform import StockTransformNode

        children_lot = [LotNode(lot, parent=self) for lot in self.data.carburelot_set.exclude(lot_status=CarbureLot.DELETED)]  # fmt:skip
        children_stock_transform = [StockTransformNode(stock, parent=self) for stock in self.data.source_stock.all()]
        return children_lot + children_stock_transform

    def diff_with_parent(self):
        if self.parent.type == Node.LOT:
            return self.get_diff(StockNode.FROM_PARENT_LOT, self.parent)
        if self.parent.type == Node.STOCK_TRANSFORM:
            # get diff with closest stock
            ancestor_stock = self.parent.get_closest(Node.STOCK)
            stock_diff = self.get_diff(StockNode.FROM_STOCK, ancestor_stock)
            # get diff with transform node
            transform_diff = self.get_diff(StockNode.FROM_PARENT_STOCK_TRANSFORM, self.parent)
            # find out the biofuel source and dest of the parent transformation
            biofuels = get_stock_transform_biofuels(self.parent.data)
            biofuel_diff = {"biofuel_id": (biofuels["destination"], self.data.biofuel_id)}
            # merge results
            return {**stock_diff, **transform_diff, **biofuel_diff}
        return {}

    def diff_with_child(self, child: Node):
        if child.type == Node.LOT:
            return self.get_diff(StockNode.FROM_CHILD_LOT, child)
        if child.type == Node.STOCK_TRANSFORM:
            # get diff with descendant stock info
            descendant_stock = child.get_first(Node.STOCK)
            stock_diff = self.get_diff(StockNode.FROM_STOCK, descendant_stock)
            # get diff with transform node
            transform_diff = self.get_diff(StockNode.FROM_CHILD_STOCK_TRANSFORM, child)
            # find out the biofuel source and dest of the parent transformation
            biofuels = get_stock_transform_biofuels(child.data)
            biofuel_diff = {"biofuel_id": (biofuels["source"], self.data.biofuel_id)}
            # merge results
            return {**stock_diff, **transform_diff, **biofuel_diff}
        return {}

    def validate(self):
        errors = []

        used_volume = 0
        available_volume = 0

        if self.parent.type == Node.LOT:
            available_volume = self.parent.data.volume
        if self.parent.type == Node.STOCK_TRANSFORM:
            available_volume = self.parent.data.volume_destination

        for child in self.children:
            if child.type == Node.LOT:
                used_volume += child.data.volume
            if child.type == Node.STOCK_TRANSFORM:
                used_volume += child.data.volume_deducted_from_source

        if used_volume > available_volume:
            info = {"available_volume": available_volume, "used_volume": used_volume}
            errors += [(self, TraceabilityError.NOT_ENOUGH_STOCK_FOR_CHILDREN, info)]

        return errors
