import { OperationList } from "accounting/types"
import { Order, Table } from "common/components/table2"
import { To } from "react-router-dom"
import { useOperationsBiofuelsColumns } from "./operations-table.columns"

type OperationTableProps = {
  rows: OperationList[]
  loading?: boolean
  order?: Order
  onOrder?: (order: Order | undefined) => void
  onClickSector?: (sector: string) => void
  rowLink?: (row: OperationList) => To
}

export const OperationTable = ({
  rows,
  loading,
  order,
  onOrder,
  onClickSector,
  rowLink,
}: OperationTableProps) => {
  const columns = useOperationsBiofuelsColumns({
    onClickSector: onClickSector ?? (() => undefined),
  })

  return (
    <Table
      columns={columns}
      rows={rows}
      rowLink={rowLink}
      loading={loading}
      order={order}
      onOrder={onOrder}
    />
  )
}
