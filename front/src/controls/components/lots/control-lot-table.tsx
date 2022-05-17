import { memo } from "react"
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
  onSelect: (selected: number[]) => void
  onAction: (lot: Lot) => void
  onOrder: (order: Order | undefined) => void
}

export const ControlTable = memo(
  ({
    loading,
    lots,
    errors,
    order,
    selected,
    onSelect,
    onAction,
    onOrder,
  }: ControlTableProps) => {
    const columns = useLotColumns()
    return (
      <Table
        loading={loading}
        order={order}
        onAction={onAction}
        onOrder={onOrder}
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
