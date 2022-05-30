import { memo } from "react"
import { To } from "react-router-dom"
import { Lot, LotError } from "transactions/types"
import Table, {
  Order,
  markerColumn,
  selectionColumn,
} from "common-v2/components/table"
import {
  getLotMarker,
  useLotColumns,
} from "transactions/components/lots/lot-table"

export interface ControlTableProps {
  loading: boolean
  lots: Lot[]
  errors: Record<number, LotError[]>
  order: Order | undefined
  selected: number[]
  rowLink: (lot: Lot) => To
  onSelect: (selected: number[]) => void
  onOrder: (order: Order | undefined) => void
}

export const ControlTable = memo(
  ({
    loading,
    lots,
    errors,
    order,
    selected,
    rowLink,
    onSelect,
    onOrder,
  }: ControlTableProps) => {
    const columns = useLotColumns()
    return (
      <Table
        loading={loading}
        order={order}
        onOrder={onOrder}
        rowLink={rowLink}
        rows={lots}
        columns={[
          markerColumn<Lot>((lot) => getLotMarker(lot, errors)),
          selectionColumn(lots, selected, onSelect, (lot) => lot.id),
          columns.score,
          columns.status,
          columns.period,
          columns.document,
          columns.volume,
          columns.feedstock,
          columns.supplier,
          columns.client,
          columns.productionSite,
          columns.depot,
          columns.ghgReduction,
        ]}
      />
    )
  }
)

export default ControlTable
