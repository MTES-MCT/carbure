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
      (
        parent.lot_id = lot.parent_lot_id
        OR parent.stock_id = lot.parent_stock_id
      )
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