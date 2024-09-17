import Table, { Order } from "common/components/table"
import { compact } from "common/utils/collection"
import { To } from "react-router-dom"
import { ChargePoint } from "../types"
import { useChargePointsColumns } from "./index.hooks"

export type ChargePointsListTableProps = {
  loading: boolean
  chargePoints: ChargePoint[]
  order?: Order
  selected: number[]
  onSelect: (selected: number[]) => void
  onOrder: (order: Order | undefined) => void
  rowLink?: (chargePoint: ChargePoint) => To
}

export const ChargePointsListTable = ({
  loading,
  order,
  onOrder,
  chargePoints,
  rowLink,
}: ChargePointsListTableProps) => {
  const columns = useChargePointsColumns()

  return (
    <Table
      loading={loading}
      order={order}
      onOrder={onOrder}
      rows={chargePoints}
      columns={compact([
        columns.status,
        columns.latest_meter_reading_date,
        columns.charge_point_id,
        columns.station_id,
        columns.current_type,
        columns.measure_energy,
        columns.is_article_2,
      ])}
      rowLink={rowLink}
    />
  )
}
