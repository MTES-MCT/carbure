from .node import Node


class StockTransformNode(Node):
    FROM_PARENT_STOCK = {
        "carbure_client_id": "entity_id",
    }

    FROM_CHILD_STOCK = {
        "carbure_supplier_id": "entity_id",
    }

    def serialize(self):
        return {
            "type": "STOCK_TRANSFORM",
            "id": self.data.id,
            "transformation_type": self.data.transformation_type,
            "volume_deducted_from_source": self.data.volume_deducted_from_source,
            "volume_destination": self.data.volume_destination,
        }

    def get_owner(self):
        return self.data.entity_id

    def get_parent(self):
        from .stock import StockNode

        return StockNode(self.data.source_stock, child=self)

    def get_children(self):
        from .stock import StockNode

        return [StockNode(stock, parent=self) for stock in self.data.carburestock_set.all()]

    def diff_with_parent(self):
        from .stock import StockNode

        if isinstance(self.parent, StockNode):
            return self.get_diff(StockTransformNode.FROM_PARENT_STOCK, self.parent)
        return {}

    def diff_with_child(self, child: Node):
        from .stock import StockNode

        if isinstance(child, StockNode):
            return self.get_diff(StockTransformNode.FROM_CHILD_STOCK, child)
        return {}
