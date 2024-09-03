import Table, { Order } from "common/components/table"
import { compact } from "common/utils/collection"
import { To } from "react-router-dom"
import { ChargePoint } from "../types"
import { useChargePointsColumns } from "./index.hooks"

type ChargePointsListTableProps = {
  loading: boolean
  chargePoints: ChargePoint[]
  order?: Order
  selected: number[]
  onSelect: (selected: number[]) => void
  onOrder: (order: Order | undefined) => void
  rowLink: (stock: ChargePoint) => To
}

export const ChargePointsListTable = ({
  loading,
  order,
  onOrder,
  rowLink,
  chargePoints,
}: ChargePointsListTableProps) => {
  const columns = useChargePointsColumns()

  return (
    <Table
      loading={loading}
      order={order}
      onOrder={onOrder}
      rowLink={rowLink}
      rows={chargePoints}
      columns={compact([
        // selectionColumn(stocks, selected, onSelect, (s: Stock) => s.id),
        columns.status,
      ])}
    />
  )
}
