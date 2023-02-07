from django.db import transaction

from .group_nodes_by_model import group_nodes_by_model
from saf.models import SafTicket, SafTicketSource
from core.traceability import LotNode, StockNode, StockTransformNode, TicketSourceNode, TicketNode
from core.models import CarbureLot, CarbureStock, CarbureStockTransformation


@transaction.atomic
def bulk_update_traceability_nodes(nodes):
    nodes_by_model = group_nodes_by_model(nodes)
    fields = get_updated_fields(nodes)

    if len(fields["lots"]) > 0:
        lots = nodes_by_model["lots"]
        lot_fields = fields["lots"]
        CarbureLot.objects.bulk_update(lots, lot_fields)

    if len(fields["stocks"]) > 0:
        stocks = nodes_by_model["stocks"]
        stock_fields = fields["stocks"]
        CarbureStock.objects.bulk_update(stocks, stock_fields)

    if len(fields["stock_transforms"]) > 0:
        stock_transforms = nodes_by_model["stock_transforms"]
        stock_transform_fields = fields["stock_transforms"]
        CarbureStockTransformation.objects.bulk_update(stock_transforms, stock_transform_fields)

    if len(fields["ticket_sources"]) > 0:
        ticket_sources = nodes_by_model["ticket_sources"]
        ticket_source_fields = fields["ticket_sources"]
        SafTicketSource.objects.bulk_update(ticket_sources, ticket_source_fields)

    if len(fields["tickets"]) > 0:
        tickets = nodes_by_model["tickets"]
        ticket_fields = fields["tickets"]
        SafTicket.objects.bulk_update(tickets, ticket_fields)

    return nodes_by_model


def get_updated_fields(nodes):
    lot_diff = {}
    stock_diff = {}
    stock_transform_diff = {}
    ticket_source_diff = {}
    ticket_diff = {}

    # merge all the diffs per type of node
    for node in nodes:
        if isinstance(node, LotNode):
            lot_diff.update(node.diff)
        if isinstance(node, StockNode):
            stock_diff.update(node.diff)
        if isinstance(node, StockTransformNode):
            stock_transform_diff.update(node.diff)
        if isinstance(node, TicketSourceNode):
            ticket_source_diff.update(node.diff)
        if isinstance(node, TicketNode):
            ticket_diff.update(node.diff)

    # extract the keys from the merged diffs
    return {
        "lots": list(lot_diff.keys()),
        "stocks": list(stock_diff.keys()),
        "stock_transforms": list(stock_transform_diff.keys()),
        "ticket_sources": list(ticket_source_diff.keys()),
        "tickets": list(ticket_diff.keys()),
    }
