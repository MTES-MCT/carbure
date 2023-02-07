from django.db import transaction

from .group_nodes_by_model import group_nodes_by_model
from saf.models import SafTicket, SafTicketSource
from core.models import CarbureLot, CarbureStock, CarbureStockTransformation


@transaction.atomic
def bulk_delete_traceability_nodes(nodes):
    nodes_by_model = group_nodes_by_model(nodes)

    print("----- %s" % nodes_by_model)

    if len(nodes_by_model["lots"]) > 0:
        lot_ids = [lot.id for lot in nodes_by_model["lots"]]
        CarbureLot.objects.filter(id__in=lot_ids).update(lot_status=CarbureLot.DELETED)

    if len(nodes_by_model["stocks"]) > 0:
        stock_ids = [stock.id for stock in nodes_by_model["stocks"]]
        CarbureStock.objects.filter(id__in=stock_ids).delete()

    if len(nodes_by_model["stock_transforms"]) > 0:
        stock_transform_ids = [stock_transform.id for stock_transform in nodes_by_model["stock_transforms"]]
        CarbureStockTransformation.objects.filter(id__in=stock_transform_ids).delete()

    if len(nodes_by_model["ticket_sources"]) > 0:
        ticket_source_ids = [ticket_source.id for ticket_source in nodes_by_model["ticket_sources"]]
        SafTicketSource.objects.filter(id__in=ticket_source_ids).delete()

    if len(nodes_by_model["tickets"]) > 0:
        ticket_ids = [ticket.id for ticket in nodes_by_model["tickets"]]
        SafTicket.objects.filter(id__in=ticket_ids).delete()

    return nodes_by_model
