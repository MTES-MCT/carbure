import React from "react"
import cl from "clsx"

import { Lots, Transaction } from "../services/types"
import { SortingSelection } from "../hooks/query/use-sort-by" // prettier-ignore

import styles from "./transaction-table.module.css"

import { useRelativePush } from "./relative-route"
import Table, { Row } from "./system/table"
import { hasErrors, hasDeadline } from "./transaction-table"
import * as C from "./transaction-columns"

type StockTableProps = {
  transactions: Lots
  sorting: SortingSelection
}

const StockTable = ({ transactions, sorting }: StockTableProps) => {
  const relativePush = useRelativePush()
  const deadline = transactions.deadlines?.date

  const columns = [
    C.empty,
    C.carbureID,
    C.biocarburant,
    C.productionSite,
    C.deliverySite,
    C.matierePremiere,
    C.ghgReduction,
    C.arrow,
  ]

  const rows: Row<Transaction>[] = transactions.lots.map((tx) => ({
    value: tx,
    onClick: () => relativePush(`${tx.id}`),
    className: cl({
      [styles.transactionRowError]: hasErrors(transactions, tx.id),
      [styles.transactionRowDeadline]: hasDeadline(tx, deadline),
    }),
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

export default StockTable
