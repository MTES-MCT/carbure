from .node import Node


class StockTransformNode(Node):
    type = Node.STOCK_TRANSFORM

    FROM_PARENT_STOCK = {
        "carbure_client": "entity",
    }

    FROM_CHILD_STOCK = {
        "carbure_client": "entity",
    }

    def get_data(self):
        return {
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
        if self.parent.type == Node.STOCK:
            return self.get_diff(StockTransformNode.FROM_PARENT_STOCK, self.parent)
        return {}

    def diff_with_child(self, child: Node):
        if child.type == Node.STOCK:
            return self.get_diff(StockTransformNode.FROM_CHILD_STOCK, child)
        return {}
