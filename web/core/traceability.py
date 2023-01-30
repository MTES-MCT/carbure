from core.models import CarbureLot


class TraceabilityError:
    NODE_HAS_DIFFERENCES_WITH_PARENT = "NODE_HAS_DIFFERENCES_WITH_PARENT"
    NOT_ENOUGH_STOCK_FOR_CHILDREN = "NOT_ENOUGH_STOCK_FOR_CHILDREN"
    NOT_ENOUGH_TICKET_SOURCE_FOR_CHILDREN = "NOT_ENOUGH_TICKET_SOURCE_FOR_CHILDREN"


class TraceabilityAccess:
    WRITE_FULL = "WRITE_FULL"  # all fields editable
    WRITE_SUSTAINABILITY = "WRITE_SUSTAINABILITY"  # only original sustainability fields editable
    WRITE_STOCK_EXTRACT = "WRITE_STOCK_EXTRACT"  # dae, volume and delivery fields editable
    WRITE_DELIVERY = "WRITE_DELIVERY"  # only delivery fields editable
    READ_ONLY = "READ_ONLY"  # no fields editable


class Node:
    def __init__(self, data, parent: "Node" = None, children: list["Node"] = None, child: "Node" = None):
        self.data = data
        self._parent = parent  # cache original parent from which this node has been created
        self._children = children  # cache an original list of children
        self._child = child  # cache original child from which this node has been created
        self._owner = None  # prepare cache for owner value
        self.diff = {}  # save the cumulative modifications applied to this node

    @property
    def parent(self) -> "Node":
        if self._parent is None:
            # cache db query results inside the instance so we don't have to run it again
            self._parent = self.get_parent()
        return self._parent

    @property
    def children(self) -> list["Node"]:
        if self._children is None:
            parent_id = id(self.parent.data) if self.parent else None
            # cache query results
            self._children = self.get_children()
            if self._child is not None:
                # in case we specified a children during initialization
                # locate the position of this child in the full list of children
                # and overwrite the new child at this position with the original child
                # so we can keep the reference to the original object in memory
                index = self.get_child_index(self._child)
                if index >= 0:
                    self._children[index] = self._child

        return self._children

    @property
    def owner(self) -> int:
        if self._owner is None:
            # cache query results
            self._owner = self.get_owner()
        return self._owner

    # returns the id of the entity owning the current node data
    def get_owner(self) -> int:
        return -1

    # return the parent of this node
    def get_parent(self) -> "Node":
        return None

    # return the list of children of this node
    def get_children(self) -> list["Node"]:
        return []

    # find the differences between this node's data and its parent's
    def diff_with_parent(self) -> dict[str, tuple]:
        return {}

    # find the differences between this node's data and one of its children
    def diff_with_child(self, child: "Node") -> dict[str, tuple]:
        return {}

    # return a simple dict representation of the node's data
    def serialize(self) -> dict:
        return {}

    # check if this node has errors
    def validate(self) -> list[tuple]:
        return []

    # return the list of fields allowed for a given access level
    def get_allowed_fields(self, access_level) -> list:
        return None

    # find the index of a given node in the children of this node
    def get_child_index(self, node: "Node") -> int:
        for i, child in enumerate(self.children):
            if type(node.data) == type(child.data) and node.data.pk == child.data.pk:
                return i
        return -1

    # return a serialized version of the tree
    def get_tree(self):
        return {
            "owner": self.owner,
            "data": self.serialize(),
            "children": [child.get_tree() for child in self.children],
        }

    # find the root of the tree of this node
    def get_root(self) -> "Node":
        if self.parent is None:
            return self

        return self.parent.get_root()

    # find the closest ancestor of this node matching the given class
    # an owner can be specified to limit results to nodes owned by this owner
    def get_closest(self, NodeType, owner=None) -> "Node":
        if owner is not None and self.owner != owner:
            return None
        if isinstance(self, NodeType):
            return self
        if self.parent is None:
            return None

        return self.parent.get_closest(NodeType, owner)

    # find the first child of this node matching the given class
    # an owner can be specified to limit results to nodes owned by this owner
    def get_first(self, NodeType, owner=None) -> "Node":
        for child in self.children:
            if owner and child.owner != owner:
                continue

            if isinstance(child, NodeType):
                return child

            first = child.get_first(NodeType, owner)

            if first is not None:
                return first

    # get the list of all the ancestors of this node, starting with its root
    def get_ancestors(self) -> list["Node"]:
        if self.parent is None:
            return []

        return self.parent.get_ancestors() + [self.parent]

    # get the list of all the descendants of this node
    def get_descendants(self) -> list["Node"]:
        descendants = self.children.copy()
        for child in self.children:
            descendants += child.get_descendants()
        return descendants

    # get all the nodes connected directly and indirectly to this one
    def get_family(self) -> list["Node"]:
        root = self.get_root()
        return [root] + root.get_descendants()

    # measure the depth of a node within the global tree
    def get_depth(self) -> int:
        return len(self.get_ancestors())

    def get_allowed_diff(self, diff: dict, entity_id):
        access_level = self.get_access_level(entity_id)

        if access_level == TraceabilityAccess.READ_ONLY:
            return {}
        if access_level == TraceabilityAccess.WRITE_FULL:
            return diff

        allowed_diff = {}
        allowed_fields = self.get_allowed_fields(access_level)

        # get_allowed_fields is not implemented on the node so we return the whole diff
        if allowed_fields is None:
            return diff

        for (field, values) in diff.items():
            if field in allowed_fields:
                allowed_diff[field] = values

        return allowed_diff

    # check if the data of this node is correctly propagated to all its descendants
    # and returns a list of errors were problems were found
    def check_integrity(self) -> list[tuple["Node", str, object]]:
        errors = self.validate()
        diff = self.diff_with_parent()

        if len(diff) > 0:
            errors = [(self, TraceabilityError.NODE_HAS_DIFFERENCES_WITH_PARENT, diff)] + errors

        for child in self.children:
            errors += child.check_integrity()

        return errors

    # update the node's data and save the diff
    def update(self, data):
        for attr, new_value in data.items():
            old_value = getattr(self.data, attr)
            if new_value != old_value:
                setattr(self.data, attr, new_value)
                self.diff[attr] = (new_value, old_value)

    # propagate the data of this node throughout the tree
    def propagate(self) -> list["Node"]:
        changed = [self]
        changed += self.propagate_down(entity_id=self.owner)
        changed += self.propagate_up(entity_id=self.owner)
        return changed

    # propagate the data of this node to its ancestors
    # and repercute it to their own descendants (except this node)
    def propagate_up(self, entity_id) -> list["Node"]:
        if not self.parent:
            return []

        changed = []

        diff = self.parent.diff_with_child(self)
        allowed_diff = self.parent.get_allowed_diff(diff, entity_id)

        if len(allowed_diff) > 0:
            self.parent.apply_diff(allowed_diff)
            changed += [self.parent]

        changed += self.parent.propagate_down(entity_id=entity_id, skip=self)
        changed += self.parent.propagate_up(entity_id=entity_id)

        return changed

    # propagate the data of this node to all its descendants
    # you can skip a child in the loop by specifying it in the params
    def propagate_down(self, entity_id, skip: "Node" = None) -> list["Node"]:
        changed = []

        for child in self.children:
            if child == skip:
                continue

            diff = child.diff_with_parent()
            allowed_diff = child.get_allowed_diff(diff, entity_id)

            if len(allowed_diff) > 0:
                child.apply_diff(allowed_diff)
                changed += [child]

            changed += child.propagate_down(entity_id=entity_id)

        return changed

    # compare this node data with the given source data
    # the map param allows mapping fields of the source data with this node's data
    def diff_data(self, source, map: dict):
        diff = {}

        for source_attr, self_attr in map.items():
            if self_attr is None:
                continue

            new_value = getattr(source, source_attr)
            old_value = getattr(self.data, self_attr)

            if new_value != old_value:
                diff[self_attr] = (new_value, old_value)

        return diff

    # apply the given diff to this node's data
    def apply_diff(self, diff: dict[str, tuple]):
        for attr, (new_value, old_value) in diff.items():
            setattr(self.data, attr, new_value)
            self.diff[attr] = (new_value, old_value)

    # check what access level an entity has over the current node
    def get_access_level(self, entity_id):
        is_node_owner = self.owner == entity_id
        is_root_owner = self.get_root().owner == entity_id
        is_stock_owner = self.get_closest(StockNode, owner=entity_id) is not None

        if is_node_owner and is_root_owner:
            return TraceabilityAccess.WRITE_FULL
        if not is_node_owner and is_root_owner:
            return TraceabilityAccess.WRITE_SUSTAINABILITY
        if is_node_owner and is_stock_owner:
            return TraceabilityAccess.WRITE_STOCK_EXTRACT
        if is_node_owner and not is_root_owner and not is_stock_owner:
            return TraceabilityAccess.WRITE_DELIVERY

        # no field editable otherwise
        return TraceabilityAccess.READ_ONLY


GHG_FIELDS = {
    "eec": "eec",
    "el": "el",
    "ep": "ep",
    "etd": "etd",
    "eu": "eu",
    "esca": "esca",
    "eccs": "eccs",
    "eccr": "eccr",
    "eee": "eee",
}


class LotNode(Node):
    LOT_TO_DISTANT_LOT = {
        "feedstock_id": "feedstock_id",
        "biofuel_id": "biofuel_id",
        "country_of_origin_id": "country_of_origin_id",
        "carbure_producer_id": "carbure_producer_id",
        "unknown_producer": "unknown_producer",
        "carbure_production_site_id": "carbure_production_site_id",
        "unknown_production_site": "unknown_production_site",
        "production_country_id": "production_country_id",
        "production_site_commissioning_date": "production_site_commissioning_date",
        "production_site_certificate": "production_site_certificate",
        "production_site_double_counting_certificate": "production_site_double_counting_certificate",
        "ghg_total": "ghg_total",
        "ghg_reference": "ghg_reference",
        "ghg_reduction": "ghg_reduction",
        "ghg_reference_red_ii": "ghg_reference_red_ii",
        "ghg_reduction_red_ii": "ghg_reduction_red_ii",
        **GHG_FIELDS,
    }

    LOT_TO_DIRECT_LOT = {
        "volume": "volume",
        "weight": "weight",
        "lhv_amount": "lhv_amount",
        "transport_document_type": "transport_document_type",
        "transport_document_reference": "transport_document_reference",
        **LOT_TO_DISTANT_LOT,
    }

    LOT_SUSTAINABILITY_FIELDS = [
        # lot data
        "feedstock",
        "biofuel",
        "country_of_origin",
        # production data
        "carbure_producer",
        "unknown_producer",
        "carbure_production_site",
        "unknown_production_site",
        "production_country",
        "production_site_commissioning_date",
        "production_site_certificate",
        "production_site_certificate_type",
        "production_site_double_counting_certificate",
        # ghg
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

    LOT_STOCK_EXTRACT_FIELDS = [
        "transport_document_reference",
        "transport_document_type",
        "volume",
        "weight",
        "lhv_amount",
    ]

    LOT_DELIVERY_FIELDS = [
        "carbure_supplier_id"
        "unknown_supplier"
        "supplier_certificate"
        "supplier_certificate_type"
        "carbure_vendor_id"
        "vendor_certificate"
        "vendor_certificate_type"
        "carbure_client_id"
        "unknown_client"
        "dispatch_date"
        "carbure_dispatch_site_id"
        "unknown_dispatch_site"
        "dispatch_site_country"
        "delivery_date"
        "carbure_delivery_site_id"
        "unknown_delivery_site"
        "delivery_site_country"
        "delivery_type",
    ]

    def serialize(self):
        return {
            "type": "LOT",
            "id": self.data.id,
            "carbure_id": self.data.carbure_id,
            "biofuel": self.data.biofuel.name,
            "volume": self.data.volume,
        }

    def get_owner(self):
        return self.data.added_by_id

    def get_parent(self):
        if self.data.parent_lot:
            return LotNode(self.data.parent_lot, child=self)
        if self.data.parent_stock:
            return StockNode(self.data.parent_stock, child=self)

    def get_children(self):
        children_lot = [LotNode(lot, parent=self) for lot in self.data.carburelot_set.exclude(lot_status=CarbureLot.DELETED)]  # fmt:skip
        children_stock = [StockNode(stock, parent=self) for stock in self.data.carburestock_set.all()]
        children_ticket_source = [TicketSourceNode(ticket_source, parent=self) for ticket_source in self.data.safticketsource_set.all()]  # fmt:skip
        return children_lot + children_stock + children_ticket_source

    def get_allowed_fields(self, access_level) -> list:
        if access_level == TraceabilityAccess.WRITE_SUSTAINABILITY:
            return LotNode.LOT_SUSTAINABILITY_FIELDS
        if access_level == TraceabilityAccess.WRITE_STOCK_EXTRACT:
            return LotNode.LOT_STOCK_EXTRACT_FIELDS + LotNode.LOT_DELIVERY_FIELDS
        if access_level == TraceabilityAccess.WRITE_DELIVERY:
            return LotNode.LOT_DELIVERY_FIELDS

    def diff_with_parent(self):
        if isinstance(self.parent, LotNode):
            return self.diff_data(self.parent.data, LotNode.LOT_TO_DIRECT_LOT)
        if isinstance(self.parent, StockNode):
            if isinstance(self.parent.parent, LotNode):
                ancestor_lot = self.parent.parent
                return self.diff_data(ancestor_lot.data, LotNode.LOT_TO_DISTANT_LOT)
            elif isinstance(self.parent.parent, StockTransformNode):
                ancestor_lot = self.parent.parent.get_closest(LotNode)
                # ignore the biofuel if the ancestor stock was transformed
                return self.diff_data(ancestor_lot.data, {**LotNode.LOT_TO_DISTANT_LOT, "biofuel_id": None})
        return {}

    def diff_with_child(self, child: Node):
        # we ignore ticket source children because they cannot be modified directly anyway
        if isinstance(child, LotNode):
            return self.diff_data(child.data, LotNode.LOT_TO_DIRECT_LOT)
        if isinstance(child, StockNode):
            descendant_lot = child.get_first(LotNode)
            return self.diff_data(descendant_lot.data, LotNode.LOT_TO_DISTANT_LOT)
        return {}


class StockNode(Node):
    LOT_TO_PARENT_STOCK = {
        "biofuel_id": "biofuel_id",
        "feedstock_id": "feedstock_id",
        "carbure_production_site_id": "carbure_production_site_id",
        "unknown_production_site": "unknown_production_site",
        "production_country_id": "production_country_id",
        "ghg_reduction": "ghg_reduction",
        "ghg_reduction_red_ii": "ghg_reduction_red_ii",
    }

    LOT_TO_CHILD_STOCK = {
        **LOT_TO_PARENT_STOCK,
        "carbure_supplier_id": "carbure_supplier_id",
        "unknown_supplier": "unknown_supplier",
        "carbure_client_id": "carbure_client_id",
        "carbure_delivery_site_id": "depot_id",
    }

    STOCK_TRANSFORM_TO_PARENT_STOCK = {}

    def serialize(self):
        return {
            "type": "STOCK",
            "id": self.data.id,
            "carbure_id": self.data.carbure_id,
            "biofuel": self.data.biofuel.name,
            "remaining_volume": self.data.remaining_volume,
        }

    def get_owner(self):
        return self.data.carbure_client_id

    def get_parent(self):
        if self.data.parent_lot:
            return LotNode(self.data.parent_lot, child=self)
        if self.data.parent_transformation:
            return StockTransformNode(self.data.parent_transformation, child=self)

    def get_children(self):
        children_lot = [LotNode(lot, parent=self) for lot in self.data.carburelot_set.exclude(lot_status=CarbureLot.DELETED)]  # fmt:skip
        children_stock_transform = [StockTransformNode(stock, parent=self) for stock in self.data.source_stock.all()]
        return children_lot + children_stock_transform

    def diff_with_parent(self):
        if isinstance(self.parent, LotNode):
            return self.diff_data(self.parent.data, StockNode.LOT_TO_CHILD_STOCK)
        if isinstance(self.parent, StockTransformNode):
            ancestor_lot = self.parent.get_closest(LotNode)
            return self.diff_data(ancestor_lot.data, {**StockNode.LOT_TO_CHILD_STOCK, "biofuel_id": None})
        return {}

    def diff_with_child(self, child: Node):
        if isinstance(child, LotNode):
            return self.diff_data(child.data, StockNode.LOT_TO_PARENT_STOCK)
        if isinstance(child, StockTransformNode):
            return self.diff_data(child.data, StockNode.STOCK_TRANSFORM_TO_PARENT_STOCK)
        return {}

    def validate(self):
        errors = []

        used_volume = 0
        available_volume = 0

        if isinstance(self.parent, LotNode):
            available_volume = self.parent.data.volume
        if isinstance(self.parent, StockTransformNode):
            available_volume = self.parent.data.volume_destination

        for child in self.children:
            if isinstance(child, LotNode):
                used_volume += child.data.volume
            if isinstance(child, StockTransformNode):
                used_volume += child.data.volume_deducted_from_source

        if used_volume > available_volume:
            info = {"available_volume": available_volume, "used_volume": used_volume}
            errors += [(self, TraceabilityError.NOT_ENOUGH_STOCK_FOR_CHILDREN, info)]

        return errors


class StockTransformNode(Node):
    STOCK_TO_CHILD_STOCK_TRANSFORM = {}
    STOCK_TO_PARENT_STOCK_TRANSFORM = {}

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
        return StockNode(self.data.source_stock, child=self)

    def get_children(self):
        return [StockNode(stock, parent=self) for stock in self.data.carburestock_set.all()]

    def diff_with_parent(self):
        if isinstance(self.parent, StockNode):
            return self.diff_data(self.parent.data, StockTransformNode.STOCK_TO_CHILD_STOCK_TRANSFORM)
        return {}

    def diff_with_child(self, child: Node):
        if isinstance(child, StockNode):
            return self.diff_data(child.data, StockTransformNode.STOCK_TO_PARENT_STOCK_TRANSFORM)
        return {}


class TicketSourceNode(Node):
    LOT_TO_CHILD_TICKET_SOURCE = {
        "year": "year",
        "period": "delivery_period",
        "volume": "total_volume",
        "feedstock_id": "feedstock_id",
        "biofuel_id": "biofuel_id",
        "country_of_origin_id": "country_of_origin_id",
        "carbure_producer_id": "carbure_producer_id",
        "unknown_producer": "unknown_producer",
        "carbure_production_site_id": "carbure_production_site_id",
        "unknown_production_site": "unknown_production_site",
        "production_country_id": "production_country_id",
        "production_site_commissioning_date": "production_site_commissioning_date",
        "ghg_total": "ghg_total",
        "ghg_reference_red_ii": "ghg_reference",
        "ghg_reduction_red_ii": "ghg_reduction",
        **GHG_FIELDS,
    }

    TICKET_TO_CHILD_TICKET_SOURCE = {
        "volume": "total_volume",
        "feedstock_id": "feedstock_id",
        "biofuel_id": "biofuel_id",
        "country_of_origin_id": "country_of_origin_id",
        "carbure_producer_id": "carbure_producer_id",
        "unknown_producer": "unknown_producer",
        "carbure_production_site_id": "carbure_production_site_id",
        "unknown_production_site": "unknown_production_site",
        "production_country_id": "production_country_id",
        "production_site_commissioning_date": "production_site_commissioning_date",
        "ghg_total": "ghg_total",
        "ghg_reference": "ghg_reference",
        "ghg_reduction": "ghg_reduction",
        **GHG_FIELDS,
    }

    def serialize(self):
        return {
            "type": "TICKET_SOURCE",
            "id": self.data.id,
            "carbure_id": self.data.carbure_id,
            "biofuel": self.data.biofuel.name,
            "total_volume": self.data.total_volume,
        }

    def get_owner(self):
        return self.data.added_by_id

    def get_parent(self):
        if self.data.parent_lot:
            return LotNode(self.data.parent_lot, child=self)
        if self.data.parent_ticket:
            return TicketNode(self.data.parent_ticket, child=self)

    def get_children(self):
        return [TicketNode(ticket, parent=self) for ticket in self.data.saf_tickets.all()]

    def diff_with_parent(self):
        if isinstance(self.parent, LotNode):
            return self.diff_data(self.parent.data, TicketSourceNode.LOT_TO_CHILD_TICKET_SOURCE)
        elif isinstance(self.parent, TicketNode):
            return self.diff_data(self.parent.data, TicketSourceNode.TICKET_TO_CHILD_TICKET_SOURCE)
        return {}

    def validate(self):
        errors = []

        used_volume = 0
        available_volume = self.data.total_volume

        for child in self.children:
            if isinstance(child, TicketNode):
                used_volume += child.data.volume

        if used_volume > available_volume:
            info = {"available_volume": available_volume, "used_volume": used_volume}
            errors += [(self, TraceabilityError.NOT_ENOUGH_TICKET_SOURCE_FOR_CHILDREN, info)]

        return errors


class TicketNode(Node):
    TICKET_SOURCE_TO_CHILD_TICKET = {
        "added_by_id": "supplier_id",
        "feedstock_id": "feedstock_id",
        "biofuel_id": "biofuel_id",
        "country_of_origin_id": "country_of_origin_id",
        "carbure_producer_id": "carbure_producer_id",
        "unknown_producer": "unknown_producer",
        "carbure_production_site_id": "carbure_production_site_id",
        "unknown_production_site": "unknown_production_site",
        "production_country_id": "production_country_id",
        "production_site_commissioning_date": "production_site_commissioning_date",
        "ghg_total": "ghg_total",
        "ghg_reference": "ghg_reference",
        "ghg_reduction": "ghg_reduction",
        **GHG_FIELDS,
    }

    def serialize(self):
        return {
            "type": "TICKET",
            "id": self.data.id,
            "carbure_id": self.data.carbure_id,
            "biofuel": self.data.biofuel.name,
            "volume": self.data.volume,
        }

    def get_owner(self):
        return self.data.supplier_id

    def get_parent(self):
        return TicketSourceNode(self.data.parent_ticket_source, child=self)

    def get_children(self):
        return [TicketSourceNode(ticket_source, parent=self) for ticket_source in self.data.safticketsource_set.all()]

    def diff_with_parent(self):
        if isinstance(self.parent, TicketSourceNode):
            return self.diff_data(self.parent.data, TicketNode.TICKET_SOURCE_TO_CHILD_TICKET)
        return {}
