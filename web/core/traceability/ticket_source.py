from .node import GHG_FIELDS, Node, TraceabilityError


class TicketSourceNode(Node):
    type = Node.TICKET_SOURCE

    FROM_PARENT_LOT = {
        "period": "delivery_period",
        "volume": "total_volume",
        "carbure_client": "added_by",
        "ghg_reference_red_ii": "ghg_reference",
        "ghg_reduction_red_ii": "ghg_reduction",
        "year": True,
        "feedstock": True,
        "biofuel": True,
        "country_of_origin": True,
        "carbure_producer": True,
        "unknown_producer": True,
        "carbure_production_site": True,
        "unknown_production_site": True,
        "production_country": True,
        "production_site_commissioning_date": True,
        "ghg_total": True,
        "id": "origin_lot_id",
        "carbure_delivery_site": "origin_lot_site",
        **GHG_FIELDS,
    }

    FROM_PARENT_TICKET = {
        "volume": "total_volume",
        "assignment_period": "delivery_period",
        "year": True,
        "feedstock": True,
        "biofuel": True,
        "country_of_origin": True,
        "carbure_producer": True,
        "unknown_producer": True,
        "carbure_production_site": True,
        "unknown_production_site": True,
        "production_country": True,
        "production_site_commissioning_date": True,
        "ghg_total": True,
        "ghg_reference": True,
        "ghg_reduction": True,
        "origin_lot": True,
        "origin_lot_site": True,
        **GHG_FIELDS,
    }

    def get_data(self):
        return {
            "carbure_id": self.data.carbure_id,
            "biofuel": self.data.biofuel.name,
            "total_volume": self.data.total_volume,
            "delivery_period": self.data.delivery_period,
        }

    def get_owner(self):
        return self.data.added_by_id

    def get_parent(self):
        from .lot import LotNode  # noqa: E402
        from .ticket import TicketNode  # noqa: E402

        if self.data.parent_lot:
            return LotNode(self.data.parent_lot, child=self)
        if self.data.parent_ticket:
            return TicketNode(self.data.parent_ticket, child=self)

    def get_children(self):
        from .ticket import TicketNode  # noqa: E402

        return [TicketNode(ticket, parent=self) for ticket in self.data.saf_tickets.all()]

    def diff_with_parent(self):
        if self.parent.type == Node.LOT:
            return self.get_diff(TicketSourceNode.FROM_PARENT_LOT, self.parent)
        elif self.parent.type == Node.TICKET:
            return self.get_diff(TicketSourceNode.FROM_PARENT_TICKET, self.parent)
        return {}

    def validate(self):
        errors = []

        used_volume = 0
        available_volume = self.data.total_volume

        for child in self.children:
            if child.type == Node.TICKET:
                used_volume += child.data.volume

        if used_volume > available_volume:
            info = {"available_volume": available_volume, "used_volume": used_volume}
            errors += [(self, TraceabilityError.NOT_ENOUGH_TICKET_SOURCE_FOR_CHILDREN, info)]

        return errors
