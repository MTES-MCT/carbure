import cl from "clsx"
import { TFunction, useTranslation } from "react-i18next"

import {
  Entity,
  EntityType,
  Lots,
  LotStatus,
  Transaction,
  UserRole,
} from "common/types"
import { SortingSelection } from "transactions/hooks/query/use-sort-by" // prettier-ignore
import { TransactionSelection } from "transactions/hooks/query/use-selection"
import { StatusSelection } from "transactions/hooks/query/use-status"

import { hasDeadline, hasErrors, hasWarnings } from "../helpers"
import { useRelativePush } from "common/components/relative-route"

import {
  AlertTriangle,
  Check,
  Copy,
  Cross,
  EyeOff,
  Pin,
} from "common/components/icons"
import Table, { Actions, arrow, Column, Row } from "common/components/table"
import * as C from "./list-columns"

import styles from "./list-table.module.css"
import { EntityDeliverySite } from "settings/hooks/use-delivery-sites"
import { useRights } from "carbure/hooks/use-rights"

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

type TxActions = Record<string, (tx: Transaction) => void> & {
  t: TFunction<"translation">
}
type TxColumn = Column<Transaction>

const getDraftActions = ({
  onValidate,
  onDuplicate,
  onDelete,
  t,
}: TxActions): TxColumn =>
  Actions([
    { icon: Check, title: t("Envoyer le lot"), action: onValidate },
    { icon: Copy, title: t("Dupliquer le lot"), action: onDuplicate },
    { icon: Cross, title: t("Supprimer le lot"), action: onDelete },
  ])

const getToFixActions = ({ onCorrect, onDelete, t }: TxActions): TxColumn =>
  Actions([
    { icon: Check, title: t("Renvoyer le lot"), action: onCorrect },
    { icon: Cross, title: t("Supprimer le lot"), action: onDelete },
  ])

const getInboxActions = ({
  onAccept,
  onComment,
  onReject,
  t,
}: TxActions): TxColumn =>
  Actions([
    { icon: Check, title: t("Accepter le lot"), action: onAccept },
    {
      icon: AlertTriangle,
      title: t("Accepter sous réserve"),
      action: onComment,
    },
    { icon: Cross, title: t("Refuser le lot"), action: onReject },
  ])

const getDuplicateActions = ({
  onDuplicate,
  t,
}: TxActions): Column<Transaction> =>
  Actions([{ icon: Copy, title: t("Dupliquer le lot"), action: onDuplicate }])

const getControlActions = ({
  onHide,
  onHighlight,
  t,
}: TxActions): Column<Transaction> =>
  Actions([
    { icon: Pin, title: t("Épingler le lot"), action: onHighlight },
    { icon: EyeOff, title: t("Ignorer le lot"), action: onHide },
  ])

type TransactionTableProps = {
  entity: Entity
  transactions: Lots
  status: StatusSelection
  sorting: SortingSelection
  outsourceddepots: EntityDeliverySite[] | undefined

  selection: TransactionSelection
  onDelete: (tx: Transaction) => void
  onValidate: (tx: Transaction) => void
  onDuplicate: (tx: Transaction) => void
  onAccept: (tx: Transaction) => void
  onComment: (tx: Transaction) => void
  onReject: (tx: Transaction) => void
  onCorrect: (tx: Transaction) => void
  onAuditorHide: (tx: Transaction) => void
  onAuditorHighlight: (tx: Transaction) => void
  onAdminHide: (tx: Transaction) => void
  onAdminHighlight: (tx: Transaction) => void
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
  onAuditorHide,
  onAuditorHighlight,
  onAdminHide,
  onAdminHighlight,
}: TransactionTableProps) => {
  const { t } = useTranslation()

  const rights = useRights()
  const relativePush = useRelativePush()
  const deadline = transactions.deadlines.date

  const isProducer = entity.entity_type === EntityType.Producer
  const isOperator = entity.entity_type === EntityType.Operator
  const isTrader = entity.entity_type === EntityType.Trader
  const isAdmin = entity.entity_type === EntityType.Administration
  const isAuditor = entity.entity_type === EntityType.Auditor

  let columns = [
    C.selector(selection),
    C.status(entity),
    C.period(transactions.deadlines.date),
  ]

  if (isProducer || isTrader) {
    columns.push(...PRODUCER_COLUMNS)
  } else if (isOperator) {
    columns.push(...OPERATOR_COLUMNS)
  } else if (isAdmin || isAuditor) {
    columns.push(...ADMIN_COLUMNS)
  }

  if (rights.is(UserRole.Auditor, UserRole.ReadOnly)) {
    columns.push(arrow)
  } else if (isAdmin) {
    columns.push(
      getControlActions({
        t,
        onHide: onAdminHide,
        onHighlight: onAdminHighlight,
      })
    )
  } else if (isAdmin || isAuditor) {
    columns.push(
      getControlActions({
        t,
        onHide: onAuditorHide,
        onHighlight: onAuditorHighlight,
      })
    )
  } else if (status.is(LotStatus.Draft)) {
    columns.push(getDraftActions({ t, onValidate, onDuplicate, onDelete }))
  } else if (status.is(LotStatus.ToFix)) {
    columns.push(getToFixActions({ t, onCorrect, onDelete }))
  } else if (status.is(LotStatus.Inbox)) {
    columns.push(getInboxActions({ t, onAccept, onComment, onReject }))
  } else if (isProducer || isTrader) {
    columns.push(getDuplicateActions({ t, onDuplicate }))
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
