import React from "react"

import { Lots, LotStatus, Transaction } from "../../services/types"
import { SortingSelection } from "../../hooks/query/use-sort-by" // prettier-ignore
import { TransactionSelection } from "../../hooks/query/use-selection"
import { StatusSelection } from "../../hooks/query/use-status"

import { useRelativePush } from "../relative-route"

import Table, { Actions, Column, Row } from "../system/table"
import * as C from "../transaction/transaction-columns"
import { Edit } from "../system/icons"
import { LotSender } from "../../hooks/actions/use-send-lots"

type A = Record<string, (id: number) => void>
type CT = Column<Transaction>

const getStockActions = ({ sendLot }: A): CT =>
  Actions([
  { icon: Edit, title: "Envoyer", action: (tx) => sendLot(tx.id) },
])

type StockTableProps = {
  stock: Lots | null
  status: StatusSelection
  sorting: SortingSelection
  selection: TransactionSelection
  sender: LotSender
}

export const StockTable = ({
  stock,
  status,
  sorting,
  selection,
  sender,
}: StockTableProps) => {
  const relativePush = useRelativePush()
  const sendLot = sender.sendLot


  const columns = []
  const default_columns = [
    C.origine,
    C.vendor,
    C.biocarburant,
    C.matierePremiere,
    C.ghgReduction,
  ]

  if (status.is(LotStatus.Draft)) {
    columns.push(C.selector(selection))
  }

  if (status.is(LotStatus.Inbox)) {
    columns.push(C.selector(selection))
    columns.push(C.carbureID)
    columns.push(C.depot)
  }

  if (status.is(LotStatus.Stock)) {
    columns.push(C.empty)
    columns.push(C.carbureID)
    columns.push(C.depot)
  }

  columns.push(...default_columns)

  if (status.is(LotStatus.Stock)) {
    columns.push(getStockActions({ sendLot }))
  }

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
