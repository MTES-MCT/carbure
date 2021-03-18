import React from "react"
import cl from "clsx"

import { Entity, EntityType, Lots, LotStatus, Transaction } from "common/types"
import { SortingSelection } from "transactions/hooks/query/use-sort-by" // prettier-ignore
import { TransactionSelection } from "transactions/hooks/query/use-selection"
import { StatusSelection } from "transactions/hooks/query/use-status"

import { hasDeadline, hasErrors, hasWarnings } from "../helpers"
import { useRelativePush } from "common/components/relative-route"

import { AlertTriangle, Check, Copy, Cross } from "common/components/icons"
import Table, { Actions, arrow, Column, Row } from "common/components/table"
import * as C from "./list-columns"

import styles from "./list-table.module.css"
import { EntityDeliverySite } from "settings/hooks/use-delivery-sites"

export const PRODUCER_COLUMNS = [
  C.dae,
  C.biocarburant,
  C.matierePremiere,
  C.client,
  C.productionSite,
  C.deliverySite,
  C.ghgReduction,
]

export const OPERATOR_COLUMNS = [
  C.dae,
  C.biocarburant,
  C.matierePremiere,
  C.vendor,
  C.productionSite,
  C.depot,
  C.ghgReduction,
]

export const ADMIN_COLUMNS = [
  C.dae,
  C.biocarburant,
  C.matierePremiere,
  C.vendor,
  C.productionSite,
  C.client,
  C.depot,
  C.addedBy,
  C.ghgReduction,
]

type A = Record<string, (id: number) => void>
type CT = Column<Transaction>

const getDraftActions = ({ onValidate, onDuplicate, onDelete }: A): CT =>
  Actions([
    { icon: Check, title: "Envoyer le lot", action: (tx) => onValidate(tx.id) },
    { icon: Copy, title: "Dupliquer le lot", action: (tx) => onDuplicate(tx.id) }, // prettier-ignore
    { icon: Cross, title: "Supprimer le lot", action: (tx) => onDelete(tx.id) },
  ])

const getToFixActions = ({ onCorrect, onDelete }: A): CT =>
  Actions([
    { icon: Check, title: "Renvoyer le lot", action: (tx) => onCorrect(tx.id) },
    { icon: Cross, title: "Supprimer le lot", action: (tx) => onDelete(tx.id) },
  ])

const getInboxActions = ({ onAccept, onComment, onReject }: A): CT =>
  Actions([
    { icon: Check, title: "Accepter le lot", action: (tx) => onAccept(tx.id) },
    { icon: AlertTriangle, title: "Accepter sous réserve", action: (tx) => onComment(tx.id) }, // prettier-ignore
    { icon: Cross, title: "Refuser le lot", action: (tx) => onReject(tx.id) },
  ])

const getDuplicateActions = ({ onDuplicate }: A): Column<Transaction> =>
  Actions([{ icon: Copy, title: "Dupliquer le lot", action: (tx) => onDuplicate(tx.id) }]) // prettier-ignore

type TransactionTableProps = {
  entity: Entity
  transactions: Lots
  status: StatusSelection
  sorting: SortingSelection
  outsourceddepots: EntityDeliverySite[] | undefined

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
  outsourceddepots,
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

  const isProducer = entity.entity_type === EntityType.Producer
  const isOperator = entity.entity_type === EntityType.Operator
  const isTrader = entity.entity_type === EntityType.Trader
  const isAdmin = entity.entity_type === EntityType.Administration

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

  columns.push(C.status(entity))
  columns.push(C.period(transactions.deadlines.date))

  if (isProducer || isTrader) {
    columns.push(...PRODUCER_COLUMNS)
  } else if (isOperator) {
    columns.push(...OPERATOR_COLUMNS)
  } else if (isAdmin) {
    columns.push(...ADMIN_COLUMNS)
  }

  if (status.is(LotStatus.Draft)) {
    columns.push(getDraftActions({ onValidate, onDuplicate, onDelete }))
  } else if (status.is(LotStatus.ToFix)) {
    columns.push(getToFixActions({ onCorrect, onDelete }))
  } else if (status.is(LotStatus.Inbox)) {
    columns.push(getInboxActions({ onAccept, onComment, onReject }))
  } else if (isProducer || isTrader) {
    columns.push(getDuplicateActions({ onDuplicate }))
  } else {
    columns.push(arrow)
  }

  const rows: Row<Transaction>[] = transactions.lots.map((tx) => ({
    value: tx,
    onClick: () => relativePush(`${tx.id}`),
    className: cl({
      [styles.transactionRowError]: hasErrors(tx, transactions.errors),
      [styles.transactionRowWarning]: hasWarnings(tx, transactions.errors),
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
