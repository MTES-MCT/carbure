class TraceabilityError:
    NODE_HAS_DIFFERENCES_WITH_PARENT = "NODE_HAS_DIFFERENCES_WITH_PARENT"
    NOT_ENOUGH_STOCK_FOR_CHILDREN = "NOT_ENOUGH_STOCK_FOR_CHILDREN"
    NOT_ENOUGH_TICKET_SOURCE_FOR_CHILDREN = "NOT_ENOUGH_TICKET_SOURCE_FOR_CHILDREN"


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

    # return the list of fields allowed for entity_id
    def get_allowed_fields(self, entity_id) -> list:
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
        allowed_diff = {}
        allowed_fields = self.get_allowed_fields(entity_id)

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
