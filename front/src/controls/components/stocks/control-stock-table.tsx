import { memo } from "react"
import { Stock } from "transactions/types"
import Table, { Order, selectionColumn } from "common-v2/components/table"
import { useStockColumns } from "transactions/components/stocks/stock-table"

export interface ControlStockTableProps {
  loading: boolean
  stocks: Stock[]
  order: Order | undefined
  selected: number[]
  onSelect: (selected: number[]) => void
  onAction: (stock: Stock) => void
  onOrder: (order: Order | undefined) => void
}

export const ControlStockTable = memo(
  ({
    loading,
    stocks,
    order,
    selected,
    onSelect,
    onAction,
    onOrder,
  }: ControlStockTableProps) => {
    const columns = useStockColumns()
    return (
      <Table
        loading={loading}
        order={order}
        onAction={onAction}
        onOrder={onOrder}
        rows={stocks}
        columns={[
          selectionColumn(stocks, selected, onSelect, (s: Stock) => s.id),
          columns.status,
          columns.period,
          columns.biofuel,
          columns.feedstock,
          columns.supplier,
          columns.productionSite,
          columns.depot,
          columns.ghgReduction,
        ]}
      />
    )
  }
)

export default ControlStockTable
