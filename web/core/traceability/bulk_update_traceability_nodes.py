from django.db import transaction

from core.models import CarbureLot, CarbureStock, CarbureStockTransformation
from core.traceability import Node
from saf.models import SafTicket, SafTicketSource
from transactions.services.carbure_id import bulk_generate_lot_carbure_id, bulk_generate_stock_carbure_id

from .group_nodes_by_type import group_nodes_by_type


@transaction.atomic
def bulk_update_traceability_nodes(nodes):
    nodes_by_type = group_nodes_by_type(nodes)
    fields = get_updated_fields(nodes)

    if len(fields[Node.LOT]) > 0:
        lots = nodes_by_type[Node.LOT]
        lot_fields = fields[Node.LOT]
        CarbureLot.objects.bulk_update(lots, lot_fields)
        bulk_generate_lot_carbure_id(CarbureLot.objects.filter(pk__in=[lot.pk for lot in lots]), save=True)

    if len(fields[Node.STOCK]) > 0:
        stocks = nodes_by_type[Node.STOCK]
        stock_fields = fields[Node.STOCK]
        CarbureStock.objects.bulk_update(stocks, stock_fields)
        bulk_generate_stock_carbure_id(CarbureStock.objects.filter(pk__in=[stock.pk for stock in stocks]), save=True)

    if len(fields[Node.STOCK_TRANSFORM]) > 0:
        stock_transforms = nodes_by_type[Node.STOCK_TRANSFORM]
        stock_transform_fields = fields[Node.STOCK_TRANSFORM]
        CarbureStockTransformation.objects.bulk_update(stock_transforms, stock_transform_fields)

    if len(fields[Node.TICKET_SOURCE]) > 0:
        ticket_sources = nodes_by_type[Node.TICKET_SOURCE]
        ticket_source_fields = fields[Node.TICKET_SOURCE]
        SafTicketSource.objects.bulk_update(ticket_sources, ticket_source_fields)

    if len(fields[Node.TICKET]) > 0:
        tickets = nodes_by_type[Node.TICKET]
        ticket_fields = fields[Node.TICKET]
        SafTicket.objects.bulk_update(tickets, ticket_fields)

    return nodes_by_type


def get_updated_fields(nodes: list[Node]):
    diffs = {
        Node.LOT: {},
        Node.STOCK: {},
        Node.STOCK_TRANSFORM: {},
        Node.TICKET_SOURCE: {},
        Node.TICKET: {},
    }

    # merge all the diffs per type of node
    for node in nodes:
        diffs[node.type].update(node.diff)

    # extract the keys from the merged diffs
    return {type: list(diff.keys()) for type, diff in diffs.items()}
