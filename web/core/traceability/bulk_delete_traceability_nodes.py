from django.db import transaction

from core.models import CarbureLot, CarbureStock, CarbureStockTransformation
from saf.models import SafTicket, SafTicketSource

from .group_nodes_by_type import group_nodes_by_type
from .node import Node


@transaction.atomic
def bulk_delete_traceability_nodes(nodes):
    nodes_by_type = group_nodes_by_type(nodes)

    if len(nodes_by_type[Node.LOT]) > 0:
        lot_ids = [lot.id for lot in nodes_by_type[Node.LOT]]
        lots = CarbureLot.objects.filter(id__in=lot_ids)
        lots.exclude(lot_status=CarbureLot.DRAFT).update(lot_status=CarbureLot.DELETED)
        lots.filter(lot_status=CarbureLot.DRAFT).delete()

    if len(nodes_by_type[Node.STOCK]) > 0:
        stock_ids = [stock.id for stock in nodes_by_type[Node.STOCK]]
        CarbureStock.objects.filter(id__in=stock_ids).delete()

    if len(nodes_by_type[Node.STOCK_TRANSFORM]) > 0:
        stock_transform_ids = [stock_transform.id for stock_transform in nodes_by_type[Node.STOCK_TRANSFORM]]
        CarbureStockTransformation.objects.filter(id__in=stock_transform_ids).delete()

    if len(nodes_by_type[Node.TICKET_SOURCE]) > 0:
        ticket_source_ids = [ticket_source.id for ticket_source in nodes_by_type[Node.TICKET_SOURCE]]
        SafTicketSource.objects.filter(id__in=ticket_source_ids).delete()

    if len(nodes_by_type[Node.TICKET]) > 0:
        ticket_ids = [ticket.id for ticket in nodes_by_type[Node.TICKET]]
        SafTicket.objects.filter(id__in=ticket_ids).delete()

    return nodes_by_type
