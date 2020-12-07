import React from "react"

import { Lots, LotStatus, Transaction } from "common/types"
import { SortingSelection } from "common/hooks/query/use-sort-by" // prettier-ignore
import { TransactionSelection } from "common/hooks/query/use-selection"
import { StatusSelection } from "common/hooks/query/use-status"

import { useRelativePush } from "common/components/relative-route"

import Table, { Actions, arrow, Column, Row } from "common/system/table"
import * as C from "transactions/components/transaction-columns"
import { Edit } from "common/system/icons"
import { LotSender } from "common/hooks/actions/use-send-lots"

type A = Record<string, (id: number) => void>
type CT = Column<Transaction>

const getStockActions = ({ createDrafts }: A): CT =>
  Actions([
    {
      icon: Edit,
      title: "Préparer l'envoi",
      action: (tx) => createDrafts(tx.id),
    },
  ])

type StockTableProps = {
  stock: Lots | null
  status: StatusSelection
  sorting: SortingSelection
  selection: TransactionSelection
  sender: LotSender
}

const COLUMNS = [C.origine, C.biocarburant, C.matierePremiere, C.ghgReduction]

export const StockTable = ({
  stock,
  status,
  sorting,
  selection,
  sender,
}: StockTableProps) => {
  const relativePush = useRelativePush()
  const createDrafts = sender.createDrafts

  const columns = []

  if (status.is(LotStatus.ToSend)) {
    columns.push(C.selector(selection))
  }

  if (status.is(LotStatus.Inbox)) {
    columns.push(C.selector(selection))
    columns.push(C.depot)
    columns.push(C.vendor)
    columns.push(C.dae)
  }

  if (status.is(LotStatus.Stock)) {
    columns.push(C.empty)
    columns.push(C.depot)
  }

  columns.push(...COLUMNS)

  if (status.is(LotStatus.ToSend)) {
    columns.push(C.dae)
    columns.push(C.client)
    columns.push(C.destination)
    columns.push(arrow)
  }

  if (status.is(LotStatus.Inbox)) {
    columns.push(arrow)
  }

  if (status.is(LotStatus.Stock)) {
    columns.push(getStockActions({ createDrafts }))
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
