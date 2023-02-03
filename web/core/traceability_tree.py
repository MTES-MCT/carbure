from core.models import CarbureLot, Biocarburant


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


ETHANOL = Biocarburant.objects.get(code="ETH").id
ETBE = Biocarburant.objects.get(code="ETBE").id


def get_stock_transform_biofuels(stock_transform):
    if stock_transform.transformation_type == "ETH_ETBE":
        return {"source": ETHANOL, "destination": ETBE}
    return {}


class Node:
    def __init__(self, data, parent: "Node" = None, children: list["Node"] = None, child: "Node" = None):
        self.data = data
        self._parent = parent  # cache original parent from which this node has been created
        self._children = children  # cache an original list of children
        self._child = child  # cache original child from which this node has been created
        self._owner = None  # prepare cache for owner value
        self.diff = {}  # save the cumulative modifications applied to this node
        self.changed_only = False  # flag to propagate only fields that were changed after an update

    @property
    def parent(self) -> "Node":
        if self._parent is None:
            # cache db query results inside the instance so we don't have to run it again
            self._parent = self.get_parent()
        return self._parent

    @property
    def children(self) -> list["Node"]:
        if self._children is None:
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

    # check if the node can be modified and apply the update
    def update(self, data, entity_id=None) -> dict:
        diff = {}

        # generate a diff dict
        for attr, new_value in data.items():
            old_value = getattr(self.data, attr)
            if new_value != old_value:
                diff[attr] = (new_value, old_value)

        # if an entity_id is specified, check if it has the right to apply the diff
        if entity_id is not None:
            allowed_diff = self.get_allowed_diff(diff, entity_id)
            if len(allowed_diff) != len(diff):
                raise Exception("Forbidden to update attributes")

        # apply the diff if everything went fine
        return self.apply_diff(diff)

    # check if the data of this node is correctly propagated to all its descendants
    # and returns a list of errors were problems were found
    def check_integrity(self) -> list[tuple["Node", str, object]]:
        # check all fields when diffing
        self.changed_only = False

        errors = self.validate()
        diff = self.diff_with_parent()

        if len(diff) > 0:
            errors = [(self, TraceabilityError.NODE_HAS_DIFFERENCES_WITH_PARENT, diff)] + errors

        for child in self.children:
            errors += child.check_integrity()

        return errors

    # propagate the data of this node throughout the tree
    def propagate(self, changed_only=False) -> list["Node"]:
        # setup the changed_only flag
        self.changed_only = changed_only

        # propagate the node up and down and list the changed nodes
        changed = [self]
        changed += self.propagate_down()
        changed += self.propagate_up()

        return changed

    # propagate the data of this node to its ancestors
    # and repercute it to their own descendants (except this node)
    def propagate_up(self) -> list["Node"]:
        if not self.parent:
            return []

        self.parent.changed_only = self.changed_only
        diff = self.parent.diff_with_child(self)

        changed_nodes = []

        if len(diff) > 0:
            self.parent.apply_diff(diff)
            changed_nodes += [self.parent]

        changed_nodes += self.parent.propagate_down(skip=self)
        changed_nodes += self.parent.propagate_up()

        return changed_nodes

    # propagate the data of this node to all its descendants
    # you can skip a child in the loop by specifying it in the params
    def propagate_down(self, skip: "Node" = None) -> list["Node"]:
        changed = []

        for child in self.children:
            if child == skip:
                continue

            child.changed_only = self.changed_only
            diff = child.diff_with_parent()

            if len(diff) > 0:
                child.apply_diff(diff)
                changed += [child]

            changed += child.propagate_down()

        return changed

    # compare this node data with the given source data
    # the map param allows mapping fields of the source data with this node's data
    def get_diff(self, map: dict, source: "Node"):
        diff = {}

        for source_attr, self_attr in map.items():
            if not self_attr:
                continue

            # skip unchanged fields when changed_only mode is active
            if self.changed_only and source_attr not in source.diff:
                continue

            # resolve the mapped field name
            self_attr = source_attr if self_attr is True else self_attr

            new_value = getattr(source.data, source_attr)
            old_value = getattr(self.data, self_attr)

            if new_value and new_value != old_value:
                diff[self_attr] = (new_value, old_value)

        return diff

    # filter the diff by only allowing the list of fields editable by entity_id
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

        for field, values in diff.items():
            if field in allowed_fields:
                allowed_diff[field] = values

        return allowed_diff

    # apply the given diff to this node's data
    def apply_diff(self, diff: dict[str, tuple]):
        for attr, (new_value, old_value) in diff.items():
            setattr(self.data, attr, new_value)
            self.diff[attr] = (new_value, old_value)
        return self.diff

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
    "eec": True,
    "el": True,
    "ep": True,
    "etd": True,
    "eu": True,
    "esca": True,
    "eccs": True,
    "eccr": True,
    "eee": True,
}


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

    LOT_SUSTAINABILITY_FIELDS = [
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
        "production_site_certificate_type",
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

    LOT_STOCK_EXTRACT_FIELDS = [
        "transport_document_reference",
        "transport_document_type",
        "volume",
        "weight",
        "lhv_amount",
    ]

    LOT_DELIVERY_FIELDS = [
        "carbure_supplier_id",
        "unknown_supplier",
        "supplier_certificate",
        "supplier_certificate_type",
        "carbure_vendor_id",
        "vendor_certificate",
        "vendor_certificate_type",
        "carbure_client_id",
        "unknown_client",
        "dispatch_date",
        "carbure_dispatch_site_id",
        "unknown_dispatch_site",
        "dispatch_site_country",
        "delivery_date",
        "carbure_delivery_site_id",
        "unknown_delivery_site",
        "delivery_site_country",
        "delivery_type",
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


class StockNode(Node):
    FROM_LOT = {
        "biofuel_id": True,
        "feedstock_id": True,
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
            return self.get_diff(StockNode.FROM_PARENT_LOT, self.parent)
        if isinstance(self.parent, StockTransformNode):
            # get diff with closest stock
            ancestor_stock = self.parent.get_closest(StockNode)
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
        if isinstance(child, LotNode):
            return self.get_diff(StockNode.FROM_CHILD_LOT, child)
        if isinstance(child, StockTransformNode):
            # get diff with descendant stock info
            descendant_stock = child.get_first(StockNode)
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
        return StockNode(self.data.source_stock, child=self)

    def get_children(self):
        return [StockNode(stock, parent=self) for stock in self.data.carburestock_set.all()]

    def diff_with_parent(self):
        if isinstance(self.parent, StockNode):
            return self.get_diff(StockTransformNode.FROM_PARENT_STOCK, self.parent)
        return {}

    def diff_with_child(self, child: Node):
        if isinstance(child, StockNode):
            return self.get_diff(StockTransformNode.FROM_CHILD_STOCK, child)
        return {}


class TicketSourceNode(Node):
    FROM_PARENT_LOT = {
        "period": "delivery_period",
        "volume": "total_volume",
        "carbure_client_id": "added_by_id",
        "ghg_reference_red_ii": "ghg_reference",
        "ghg_reduction_red_ii": "ghg_reduction",
        "year": True,
        "feedstock_id": True,
        "biofuel_id": True,
        "country_of_origin_id": True,
        "carbure_producer_id": True,
        "unknown_producer": True,
        "carbure_production_site_id": True,
        "unknown_production_site": True,
        "production_country_id": True,
        "production_site_commissioning_date": True,
        "ghg_total": True,
        **GHG_FIELDS,
    }

    FROM_PARENT_TICKET = {
        "volume": "total_volume",
        "assignment_period": "delivery_period",
        "year": True,
        "feedstock_id": True,
        "biofuel_id": True,
        "country_of_origin_id": True,
        "carbure_producer_id": True,
        "unknown_producer": True,
        "carbure_production_site_id": True,
        "unknown_production_site": True,
        "production_country_id": True,
        "production_site_commissioning_date": True,
        "ghg_total": True,
        "ghg_reference": True,
        "ghg_reduction": True,
        **GHG_FIELDS,
    }

    def serialize(self):
        return {
            "type": "TICKET_SOURCE",
            "id": self.data.id,
            "carbure_id": self.data.carbure_id,
            "biofuel": self.data.biofuel.name,
            "total_volume": self.data.total_volume,
            "delivery_period": self.data.delivery_period,
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
            return self.get_diff(TicketSourceNode.FROM_PARENT_LOT, self.parent)
        elif isinstance(self.parent, TicketNode):
            return self.get_diff(TicketSourceNode.FROM_PARENT_TICKET, self.parent)
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
    FROM_PARENT_TICKET_SOURCE = {
        "added_by_id": "supplier_id",
        "feedstock_id": True,
        "biofuel_id": True,
        "country_of_origin_id": True,
        "carbure_producer_id": True,
        "unknown_producer": True,
        "carbure_production_site_id": True,
        "unknown_production_site": True,
        "production_country_id": True,
        "production_site_commissioning_date": True,
        "ghg_total": True,
        "ghg_reference": True,
        "ghg_reduction": True,
        **GHG_FIELDS,
    }

    def serialize(self):
        return {
            "type": "TICKET",
            "id": self.data.id,
            "carbure_id": self.data.carbure_id,
            "biofuel": self.data.biofuel.name,
            "volume": self.data.volume,
            "assignment_period": self.data.assignment_period,
        }

    def get_owner(self):
        return self.data.supplier_id

    def get_parent(self):
        return TicketSourceNode(self.data.parent_ticket_source, child=self)

    def get_children(self):
        return [TicketSourceNode(ticket_source, parent=self) for ticket_source in self.data.safticketsource_set.all()]

    def diff_with_parent(self):
        if isinstance(self.parent, TicketSourceNode):
            return self.get_diff(TicketNode.FROM_PARENT_TICKET_SOURCE, self.parent)
        return {}
