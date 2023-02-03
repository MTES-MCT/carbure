from .node import Node, GHG_FIELDS


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
        from .ticket_source import TicketSourceNode

        return TicketSourceNode(self.data.parent_ticket_source, child=self)

    def get_children(self):
        from .ticket_source import TicketSourceNode

        return [TicketSourceNode(ticket_source, parent=self) for ticket_source in self.data.safticketsource_set.all()]

    def diff_with_parent(self):
        from .ticket_source import TicketSourceNode

        if isinstance(self.parent, TicketSourceNode):
            return self.get_diff(TicketNode.FROM_PARENT_TICKET_SOURCE, self.parent)
        return {}
