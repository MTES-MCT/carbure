import React from "react"

import { Lots, LotStatus, Transaction } from "../../services/types"
import { SortingSelection } from "../../hooks/query/use-sort-by" // prettier-ignore
import { TransactionSelection } from "../../hooks/query/use-selection"
import { StatusSelection } from "../../hooks/query/use-status"

import { useRelativePush } from "../relative-route"

import Table, { Row } from "../system/table"
import * as C from "../transaction/transaction-columns"

type StockTableProps = {
  stock: Lots | null
  status: StatusSelection
  sorting: SortingSelection
  selection: TransactionSelection
}

export const StockTable = ({
  stock,
  status,
  sorting,
  selection,
}: StockTableProps) => {
  const relativePush = useRelativePush()

  const columns = []
  const default_columns = [
    C.status,
    C.origine,
    C.biocarburant,
    C.matierePremiere,
    C.client,
    C.deliverySite,
    C.ghgReduction,
  ]

  if (status.is(LotStatus.Draft)) {
    columns.push(C.selector(selection))
  }

  if (status.is(LotStatus.Inbox)) {
    columns.push(C.selector(selection))
    columns.push(C.carbureID)
  }

  if (status.is(LotStatus.Stock)) {
    columns.push(C.empty)
    columns.push(C.carbureID)
  }

  columns.push(...default_columns)

  if (stock === null) {
    return null
  }

  const rows: Row<Transaction>[] = stock.lots.map((tx) => ({
    value: tx,
    onClick: () => relativePush(`${tx.id}`),
  }))

  return (
    <Table
      columns={columns}
      rows={rows}
      sortBy={sorting.column}
      order={sorting.order}
      onSort={sorting.sortBy}
    />
  )
}
