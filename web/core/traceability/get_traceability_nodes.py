from typing import Iterable

from core.models import CarbureLot, CarbureStock, CarbureStockTransformation
from core.traceability import LotNode, StockNode, StockTransformNode, TicketNode, TicketSourceNode
from core.utils import run_query
from saf.models import SafTicket, SafTicketSource


# use a recursive query to quickly fetch the whole families of the given lots
# and build the traceability nodes and their relations based on the results
def get_traceability_nodes(lots: Iterable):
    if len(lots) == 0:
        return []

    # extract lots ids
    original_lot_ids = [lot.id for lot in lots]

    # query the database for all the nodes related to these lots
    rows = run_query("core/traceability/get_traceability_nodes.sql", original_lot_ids)

    # fetch all the models for the listed ids
    models_by_type = query_models_by_type(rows)

    # connect all the models together through Nodes
    lot_nodes = connect_traceability_nodes(rows, models_by_type)

    # return only the nodes for the originally given lots
    return [lot_nodes[lot_id] for lot_id in original_lot_ids if lot_id in lot_nodes]


# list all the models referenced in the rows, grouped by their types
def query_models_by_type(rows):
    lot_ids: list[int] = []
    stock_ids: list[int] = []
    stock_transform_ids: list[int] = []
    ticket_source_ids: list[int] = []
    ticket_ids: list[int] = []

    # extract the list of ids and group them by types
    for row in rows:
        lot_id = row[0]
        stock_id = row[1]
        stock_transform_id = row[2]
        ticket_source_id = row[3]
        ticket_id = row[4]

        if lot_id is not None:
            lot_ids.append(lot_id)
        if stock_id is not None:
            stock_ids.append(stock_id)
        if stock_transform_id is not None:
            stock_transform_ids.append(stock_transform_id)
        if ticket_source_id is not None:
            ticket_source_ids.append(ticket_source_id)
        if ticket_id is not None:
            ticket_ids.append(ticket_id)

    # query the database for all of these records
    stocks = CarbureStock.objects.filter(id__in=stock_ids).select_related("biofuel")
    stock_transforms = CarbureStockTransformation.objects.filter(id__in=stock_transform_ids)
    ticket_sources = SafTicketSource.objects.filter(id__in=ticket_source_ids).select_related("biofuel")
    tickets = SafTicket.objects.filter(id__in=ticket_ids).select_related("biofuel")

    lots = CarbureLot.objects.filter(id__in=lot_ids).select_related(
        "carbure_producer",
        "carbure_supplier",
        "carbure_client",
        "added_by",
        "carbure_production_site",
        "carbure_production_site__created_by",
        "carbure_production_site__country",
        "production_country",
        "carbure_dispatch_site",
        "carbure_dispatch_site__country",
        "dispatch_site_country",
        "carbure_delivery_site",
        "carbure_delivery_site__country",
        "delivery_site_country",
        "feedstock",
        "biofuel",
        "country_of_origin",
        "parent_stock",
        "parent_lot",
    )

    return lots, stocks, stock_transforms, ticket_sources, tickets


# create nodes for all the models and set the parent/child relations between them
def connect_traceability_nodes(rows, models_by_type):
    lots, stocks, stock_transforms, ticket_sources, tickets = models_by_type

    # create individual nodes based on the results of the previous queries and index them by their type and id
    lot_nodes = {lot.id: LotNode(lot) for lot in lots}
    stock_nodes = {stock.id: StockNode(stock) for stock in stocks}
    stock_transform_nodes = {stock_transform.id: StockTransformNode(stock_transform) for stock_transform in stock_transforms}
    ticket_source_nodes = {ticket_source.id: TicketSourceNode(ticket_source) for ticket_source in ticket_sources}
    ticket_nodes = {ticket.id: TicketNode(ticket) for ticket in tickets}

    # connect these nodes together by referencing their parents and children
    for row in rows:
        node = None
        parent_node = None

        # extract node id from the row
        lot_id = row[0]
        stock_id = row[1]
        stock_transform_id = row[2]
        ticket_source_id = row[3]
        ticket_id = row[4]

        # grab the right node from the dicts
        if lot_id is not None:
            node = lot_nodes[lot_id]
        if stock_id is not None:
            node = stock_nodes[stock_id]
        if stock_transform_id is not None:
            node = stock_transform_nodes[stock_transform_id]
        if ticket_source_id is not None:
            node = ticket_source_nodes[ticket_source_id]
        if ticket_id is not None:
            node = ticket_nodes[ticket_id]

        # extract parent id from the row
        parent_lot_id = row[5]
        parent_stock_id = row[6]
        parent_stock_transform_id = row[7]
        parent_ticket_source_id = row[8]
        parent_ticket_id = row[9]

        # grab the right parent node from the dicts
        if parent_lot_id is not None:
            parent_node = lot_nodes[parent_lot_id]
        if parent_stock_id is not None:
            parent_node = stock_nodes[parent_stock_id]
        if parent_stock_transform_id is not None:
            parent_node = stock_transform_nodes[parent_stock_transform_id]
        if parent_ticket_source_id is not None:
            parent_node = ticket_source_nodes[parent_ticket_source_id]
        if parent_ticket_id is not None:
            parent_node = ticket_nodes[parent_ticket_id]

        # initialize the node's children
        if node._children is None:
            node._children = []

        # skip the rest if the node is a root
        if parent_node is None:
            continue

        # initialize the parent's children
        if parent_node._children is None:
            parent_node._children = []

        # associate the child and its parent
        node._parent = parent_node
        parent_node._children.append(node)

    return lot_nodes
