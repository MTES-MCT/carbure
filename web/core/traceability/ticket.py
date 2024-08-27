from .node import GHG_FIELDS, Node


class TicketNode(Node):
    type = Node.TICKET

    FROM_PARENT_TICKET_SOURCE = {
        "added_by": "supplier",
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
        **GHG_FIELDS,
    }

    def get_data(self):
        return {
            "carbure_id": self.data.carbure_id,
            "biofuel": self.data.biofuel.name,
            "volume": self.data.volume,
            "assignment_period": self.data.assignment_period,
        }

    def get_owner(self):
        return self.data.supplier_id

    def get_parent(self):
        from .ticket_source import TicketSourceNode  # noqa: E402

        return TicketSourceNode(self.data.parent_ticket_source, child=self)

    def get_children(self):
        from .ticket_source import TicketSourceNode  # noqa: E402

        return [TicketSourceNode(ticket_source, parent=self) for ticket_source in self.data.safticketsource_set.all()]

    def diff_with_parent(self):
        if self.parent.type == Node.TICKET_SOURCE:
            return self.get_diff(TicketNode.FROM_PARENT_TICKET_SOURCE, self.parent)
        return {}
