import React from "react"
import cl from "clsx"
import differenceInCalendarMonths from "date-fns/differenceInCalendarMonths"

import { Entity, Lots, LotStatus, Transaction } from "../services/types"
import { SortingSelection } from "../hooks/query/use-sort-by" // prettier-ignore
import { TransactionSelection } from "../hooks/query/use-selection"
import { StatusSelection } from "../hooks/query/use-status"

import styles from "./transaction-table.module.css"

import { useRelativePush } from "./relative-route"

import { AlertTriangle, Check, Copy, Cross } from "./system/icons"
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

const getToFixActions = ({ onCorrect, onDelete }: Actions) =>
  C.actions([
    { icon: Check, title: "Renvoyer le lot", action: onCorrect },
    { icon: Cross, title: "Supprimer le lot", action: onDelete },
  ])

const getInboxActions = ({ onAccept, onComment, onReject }: Actions) =>
  C.actions([
    { icon: Check, title: "Accepter le lot", action: onAccept },
    { icon: AlertTriangle, title: "Accepter sous réserve", action: onComment },
    { icon: Cross, title: "Refuser le lot", action: onReject },
  ])

const getDuplicateActions = ({ onDuplicate }: Actions) =>
  C.actions([{ icon: Copy, title: "Dupliquer le lot", action: onDuplicate }])

export function hasDeadline(tx: Transaction, deadline: string): boolean {
  if (!tx || tx.lot.status !== "Draft") return false

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
  onCorrect: (id: number) => void
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
  onCorrect,
}: TransactionTableProps) => {
  const relativePush = useRelativePush()
  const deadline = transactions.deadlines.date

  const isProducer = entity.entity_type === "Producteur"
  const isOperator = entity.entity_type === "Opérateur"

  let columns = []

  if (
    status.is(LotStatus.Draft) ||
    status.is(LotStatus.Inbox) ||
    status.is(LotStatus.ToFix)
  ) {
    columns.push(C.selector(selection))
  } else {
    columns.push(C.empty)
  }

  if (isProducer) {
    columns.push(...PRODUCER_COLUMNS)
  } else if (isOperator) {
    columns.push(...OPERATOR_COLUMNS)
  }

  if (status.is(LotStatus.Draft)) {
    columns.push(getDraftActions({ onValidate, onDuplicate, onDelete }))
  } else if (status.is(LotStatus.ToFix)) {
    columns.push(getToFixActions({ onCorrect, onDelete }))
  } else if (status.is(LotStatus.Inbox)) {
    columns.push(getInboxActions({ onAccept, onComment, onReject }))
  } else if (isProducer) {
    columns.push(getDuplicateActions({ onDuplicate }))
  } else {
    columns.push(C.arrow)
  }

  const rows: Row<Transaction>[] = transactions.lots.map((tx) => ({
    value: tx,
    onClick: () => relativePush(`${tx.id}`),
    className: cl({
      [styles.transactionRowError]: tx.id in transactions.errors,
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
  stock: Lots | null
  status: StatusSelection
  sorting: SortingSelection
  selection: TransactionSelection
}

export const StockTable = ({ stock, status, sorting, selection }: StockTableProps) => {
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
    console.log("Stock null")
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
