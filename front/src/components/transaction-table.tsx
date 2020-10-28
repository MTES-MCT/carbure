import React from "react"
import cl from "clsx"
import differenceInCalendarMonths from "date-fns/differenceInCalendarMonths"

import { Entity, Lots, LotStatus, Transaction } from "../services/types"
import { SortingSelection } from "../hooks/query/use-sort-by" // prettier-ignore
import { TransactionSelection } from "../hooks/query/use-selection"
import { StatusSelection } from "../hooks/query/use-status"

import styles from "./transaction-table.module.css"

import { useRelativePush } from "./relative-route"

import { Check, Copy, Cross } from "./system/icons"
import Table, { Row } from "./system/table"
import * as C from "./transaction-columns"

export const PRODUCER_COLUMNS = [
  C.status,
  C.period,
  C.dae,
  C.biocarburant,
  C.matierePremiere,
  C.client,
  C.productionSite,
  C.deliverySite,
  C.ghgReduction,
]

export const OPERATOR_COLUMNS = [
  C.status,
  C.period,
  C.dae,
  C.biocarburant,
  C.matierePremiere,
  C.vendor,
  C.productionSite,
  C.deliverySite,
  C.ghgReduction,
]

type Actions = Record<string, (id: number) => void>

const getDraftActions = ({ onValidate, onDuplicate, onDelete }: Actions) =>
  C.actions([
    { icon: Check, title: "Envoyer le lot", action: onValidate },
    { icon: Copy, title: "Dupliquer le lot", action: onDuplicate },
    { icon: Cross, title: "Supprimer le lot", action: onDelete },
  ])

const getInboxActions = ({ onAccept, onComment, onReject }: Actions) =>
  C.actions([
    { icon: Check, title: "Accepter le lot", action: onAccept },
    { icon: Copy, title: "Accepter sous réserve", action: onComment },
    { icon: Cross, title: "Refuser le lot", action: onReject },
  ])

export function hasErrors(transactions: Lots, id: number): boolean {
  return (
    transactions.lots_errors[id]?.length > 0 ||
    transactions.tx_errors[id]?.length > 0
  )
}

export function hasDeadline(tx: Transaction, deadline: string): boolean {
  if (!tx || tx.status !== LotStatus.Draft) return false

  const deadlineDate = new Date(deadline)
  const deliveryDate = new Date(tx?.delivery_date)
  return differenceInCalendarMonths(deadlineDate, deliveryDate) === 1
}

type TransactionTableProps = {
  entity: Entity
  transactions: Lots
  status: StatusSelection
  sorting: SortingSelection
  selection: TransactionSelection
  onDelete: (id: number) => void
  onValidate: (id: number) => void
  onDuplicate: (id: number) => void
  onAccept: (id: number) => void
  onComment: (id: number) => void
  onReject: (id: number) => void
}

export const TransactionTable = ({
  entity,
  transactions,
  status,
  sorting,
  selection,
  onDelete,
  onDuplicate,
  onValidate,
  onAccept,
  onComment,
  onReject,
}: TransactionTableProps) => {
  const relativePush = useRelativePush()
  const deadline = transactions.deadlines.date

  let columns = []

  if (status.active === LotStatus.Draft || status.active === LotStatus.Inbox) {
    columns.push(C.selector(selection))
  } else {
    columns.push(C.empty)
  }

  if (entity.entity_type === "Producteur") {
    columns.push(...PRODUCER_COLUMNS)
  } else if (entity.entity_type === "Opérateur") {
    columns.push(...OPERATOR_COLUMNS)
  }

  if (status.active === LotStatus.Draft) {
    columns.push(getDraftActions({ onValidate, onDuplicate, onDelete }))
  } else if (status.active === LotStatus.Inbox) {
    columns.push(getInboxActions({ onAccept, onComment, onReject }))
  } else {
    columns.push(C.arrow)
  }

  const rows: Row<Transaction>[] = transactions.lots.map((tx) => ({
    value: tx,
    onClick: () => relativePush(`${tx.id}`),
    className: cl({
      [styles.transactionRowError]: tx.errors.length > 0,
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

type StockTableProps = {
  transactions: Lots
  sorting: SortingSelection
}

export const StockTable = ({ transactions, sorting }: StockTableProps) => {
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
