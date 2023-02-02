from django.db import connection

from core.models import CarbureLot, CarbureStock, CarbureStockTransformation
from core.traceability_tree import LotNode, StockNode, StockTransformNode, TicketSourceNode, TicketNode
from saf.models import SafTicket, SafTicketSource


def get_lots_family_trees(lots: list):
    with connection.cursor() as cursor:
        lot_ids: list[int] = []
        stock_ids: list[int] = []
        stock_transform_ids: list[int] = []
        ticket_source_ids: list[int] = []
        ticket_ids: list[int] = []

        # extract lots ids
        original_lot_ids = [lot.id for lot in lots]

        # recursively query for the whole family trees for the given lot ids
        cursor.execute(LOT_FAMILY_QUERY, [original_lot_ids])

        # grab the list of results in the form of an array of tuples
        rows = cursor.fetchall()

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
            "carbure_production_site__producer",
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

        # create individual nodes based on the results of the previous queries
        lot_nodes = {lot.id: LotNode(lot) for lot in lots.iterator()}
        stock_nodes = {stock.id: StockNode(stock) for stock in stocks.iterator()}
        stock_transform_nodes = {stock_transform.id: StockTransformNode(stock_transform) for stock_transform in stock_transforms.iterator()}  # fmt:skip
        ticket_source_nodes = {ticket_source.id: TicketSourceNode(ticket_source) for ticket_source in ticket_sources.iterator()}  # fmt:skip
        ticket_nodes = {ticket.id: TicketNode(ticket) for ticket in tickets}

        # connect these nodes together by referencing their parents and children
        for row in rows:
            node = None
            parent_node = None

            # extract data from the row
            lot_id = row[0]
            stock_id = row[1]
            stock_transform_id = row[2]
            ticket_source_id = row[3]
            ticket_id = row[4]
            parent_lot_id = row[5]
            parent_stock_id = row[6]
            parent_stock_transform_id = row[7]
            parent_ticket_source_id = row[8]
            parent_ticket_id = row[9]

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

        return [lot_nodes[lot_id] for lot_id in original_lot_ids if lot_id in lot_nodes]


# this is a recursive query that starts by going up the tree
# in order to find the root nodes for the given lots ids
# and then goes down the tree to find all the nested children of these roots
LOT_FAMILY_QUERY = """
WITH RECURSIVE ancestors as (
  SELECT id lot_id,
    CAST(NULL AS SIGNED) stock_id,
    CAST(NULL AS SIGNED) stock_transform_id,
    CAST(NULL AS SIGNED) ticket_source_id,
    CAST(NULL AS SIGNED) ticket_id,
    parent_lot_id,
    parent_stock_id,
    CAST(NULL AS SIGNED) parent_transformation_id,
    CAST(NULL AS SIGNED) parent_ticket_source_id,
    CAST(NULL AS SIGNED) parent_ticket_id
  FROM carbure_lots
  WHERE id IN %s
    AND lot_status != "DELETED"
  UNION
  --
  SELECT lot.id lot_id,
  NULL stock_id,
  NULL stock_transform_id,
  NULL ticket_source_id,
  NULL ticket_id,
  lot.parent_lot_id,
  lot.parent_stock_id,
  NULL parent_transformation_id,
  NULL parent_ticket_source_id,
  NULL parent_ticket_id
  FROM ancestors child
    JOIN carbure_lots lot ON (
      child.parent_lot_id = lot.id
      AND lot.lot_status != "DELETED"
    )
  UNION
  --
  SELECT NULL lot_id,
  stock.id stock_id,
  NULL stock_transform_id,
  NULL ticket_source_id,
  NULL ticket_id,
  stock.parent_lot_id,
  NULL parent_stock_id,
  stock.parent_transformation_id,
  NULL parent_ticket_source_id,
  NULL parent_ticket_id
  FROM ancestors child
    JOIN carbure_stock stock ON child.parent_stock_id = stock.id
  UNION
  --
  SELECT NULL lot_id,
  NULL stock_id,
  stock_transform.id stock_transform_id,
  NULL ticket_source_id,
  NULL ticket_id,
  NULL parent_lot_id,
  stock_transform.source_stock_id parent_stock_id,
  NULL parent_transformation_id,
  NULL parent_ticket_source_id,
  NULL parent_ticket_id
  FROM ancestors child
    JOIN carbure_stock_transformations stock_transform ON child.parent_transformation_id = stock_transform.id
  UNION
  --
  SELECT NULL lot_id,
  NULL stock_id,
  NULL stock_transform_id,
  ticket_source.id ticket_source_id,
  NULL ticket_id,
  ticket_source.parent_lot_id,
  NULL parent_stock_id,
  NULL parent_transformation_id,
  NULL parent_ticket_source_id,
  ticket_source.parent_ticket_id
  FROM ancestors child
    JOIN saf_ticket_source ticket_source ON child.parent_ticket_source_id = ticket_source.id
  UNION
  --
  SELECT NULL lot_id,
  NULL stock_id,
  NULL stock_transform_id,
  NULL ticket_source_id,
  ticket.id ticket_id,
  NULL parent_lot_id,
  NULL parent_stock_id,
  NULL parent_transformation_id,
  ticket.parent_ticket_source_id,
  NULL parent_ticket_id
  FROM ancestors child
    JOIN saf_ticket ticket ON child.parent_ticket_id = ticket.id
),
descendants as (
  SELECT *
  FROM ancestors
  WHERE parent_lot_id IS NULL
    AND parent_stock_id IS NULL
    AND parent_transformation_id IS NULL
    AND parent_ticket_source_id IS NULL
    AND parent_ticket_id IS NULL
  UNION
  --
  SELECT lot.id lot_id,
  NULL stock_id,
  NULL stock_transform_id,
  NULL ticket_source_id,
  NULL ticket_id,
  lot.parent_lot_id,
  lot.parent_stock_id,
  NULL parent_transformation_id,
  NULL parent_ticket_source_id,
  NULL parent_ticket_id
  FROM descendants parent
    JOIN carbure_lots lot ON (
      (parent.lot_id = lot.parent_lot_id OR parent.stock_id = lot.parent_stock_id)
      AND lot.lot_status != "DELETED"
    )
  UNION
  --
  SELECT NULL lot_id,
  stock.id stock_id,
  NULL stock_transform_id,
  NULL ticket_source_id,
  NULL ticket_id,
  stock.parent_lot_id,
  NULL parent_stock_id,
  stock.parent_transformation_id,
  NULL parent_ticket_source_id,
  NULL parent_ticket_id
  FROM descendants parent
    JOIN carbure_stock stock ON (
      parent.lot_id = stock.parent_lot_id
      OR parent.stock_transform_id = stock.parent_transformation_id
    )
  UNION
  --
  SELECT NULL lot_id,
  NULL stock_id,
  stock_transform.id stock_transform_id,
  NULL ticket_source_id,
  NULL ticket_id,
  NULL parent_lot_id,
  stock_transform.source_stock_id parent_stock_id,
  NULL parent_transformation_id,
  NULL parent_ticket_source_id,
  NULL parent_ticket_id
  FROM descendants parent
    JOIN carbure_stock_transformations stock_transform ON parent.stock_id = stock_transform.source_stock_id
  UNION
  --
  SELECT NULL lot_id,
  NULL stock_id,
  NULL stock_transform_id,
  ticket_source.id ticket_source_id,
  NULL ticket_id,
  ticket_source.parent_lot_id,
  NULL parent_stock_id,
  NULL parent_transformation_id,
  NULL parent_ticket_source_id,
  ticket_source.parent_ticket_id
  FROM descendants parent
    JOIN saf_ticket_source ticket_source ON (
      parent.lot_id = ticket_source.parent_lot_id
      OR parent.ticket_id = ticket_source.parent_ticket_id
    )
  UNION
  --
  SELECT NULL lot_id,
  NULL stock_id,
  NULL stock_transform_id,
  NULL ticket_source_id,
  ticket.id ticket_id,
  NULL parent_lot_id,
  NULL parent_stock_id,
  NULL parent_transformation_id,
  ticket.parent_ticket_source_id,
  NULL parent_ticket_id
  FROM descendants parent
    JOIN saf_ticket ticket ON parent.ticket_source_id = ticket.parent_ticket_source_id
)
SELECT *
FROM descendants
"""
