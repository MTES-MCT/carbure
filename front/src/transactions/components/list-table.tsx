import cl from "clsx"
import { TFunction, useTranslation } from "react-i18next"
import { useNavigate } from "react-router-dom"

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

import {
  AlertTriangle,
  Check,
  Copy,
  Cross,
  Eye,
  EyeOff,
  Pin,
  PinOff,
  ChevronRight,
} from "common/components/icons"
import Table, { Actions, arrow, Column, Row } from "common/components/table"
import * as C from "./list-columns"

import styles from "./list-table.module.css"
import { EntityDeliverySite } from "settings/hooks/use-delivery-sites"
import { useRights } from "carbure/hooks/entity"

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

const getToFixActions = (
  { onCorrect, onDelete, t }: TxActions,
  entity: Entity
): TxColumn =>
  Actions((tx) => {
    // no actions if the entity does not own the tx
    if (
      tx.carbure_vendor?.id !== entity.id &&
      tx.lot.added_by?.id !== entity.id
    ) {
      return [{ icon: ChevronRight, title: "", action: () => {} }]
    }

    return [
      { icon: Check, title: t("Renvoyer le lot"), action: onCorrect },
      { icon: Cross, title: t("Supprimer le lot"), action: onDelete },
    ]
  })

const getInboxActions = ({
  onAccept,
  onComment,
  onReject,
  t,
}: TxActions): TxColumn =>
  Actions([
    { icon: Check, title: t("Accepter le lot"), action: onAccept },
    { icon: AlertTriangle, title: t("Accepter sous réserve"), action: onComment }, // prettier-ignore
    { icon: Cross, title: t("Refuser le lot"), action: onReject },
  ])

const getDuplicateActions = ({
  onDuplicate,
  t,
}: TxActions): Column<Transaction> =>
  Actions([{ icon: Copy, title: t("Dupliquer le lot"), action: onDuplicate }])

const getAdminActions = ({
  onHide,
  onHighlight,
  t,
}: TxActions): Column<Transaction> =>
  Actions((tx) => [
    {
      icon: tx.highlighted_by_admin ? PinOff : Pin,
      title: tx.highlighted_by_admin ? t("Désépingler le lot") : t("Épingler le lot"), // prettier-ignore
      action: onHighlight,
    },
    {
      icon: tx.hidden_by_admin ? Eye : EyeOff,
      title: tx.hidden_by_admin ? t("Montrer le lot") : t("Ignorer le lot"),
      action: onHide,
    },
  ])

const getAuditorActions = ({
  onHide,
  onHighlight,
  t,
}: TxActions): Column<Transaction> =>
  Actions((tx) => [
    {
      icon: tx.highlighted_by_auditor ? PinOff : Pin,
      title: tx.highlighted_by_auditor ? t("Désépingler le lot") : t("Épingler le lot"), // prettier-ignore
      action: onHighlight,
    },
    {
      icon: tx.hidden_by_auditor ? Eye : EyeOff,
      title: tx.hidden_by_auditor ? t("Montrer le lot") : t("Ignorer le lot"),
      action: onHide,
    },
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
  const navigate = useNavigate()
  const deadline = transactions.deadlines.date

  const isProducer = entity.entity_type === EntityType.Producer
  const isOperator = entity.entity_type === EntityType.Operator
  const isTrader = entity.entity_type === EntityType.Trader
  const isAdmin = entity.entity_type === EntityType.Administration
  const isAuditor = entity.entity_type === EntityType.Auditor

  let columns = [
    C.selector(selection),
    C.status(entity, t),
    C.period(transactions.deadlines.date, t),
  ]

  if (isProducer || isTrader) {
    columns.push(
      C.dae(t),
      C.biocarburant(t),
      C.matierePremiere(t),
      C.client(t),
      C.productionSite(t),
      C.deliverySite(t),
      C.ghgReduction(t)
    )
  } else if (isOperator) {
    columns.push(
      C.dae(t),
      C.biocarburant(t),
      C.matierePremiere(t),
      C.vendor(t),
      C.productionSite(t),
      C.depot(t),
      C.ghgReduction(t)
    )
  } else if (isAdmin || isAuditor) {
    columns.push(
      C.dae(t),
      C.biocarburant(t),
      C.matierePremiere(t),
      C.vendor(t),
      C.productionSite(t),
      C.client(t),
      C.depot(t),
      C.addedBy(t),
      C.ghgReduction(t)
    )
  }

  if (rights.is(UserRole.Auditor, UserRole.ReadOnly)) {
    columns.push(arrow)
  } else if (isAdmin) {
    columns.push(
      getAdminActions({
        t,
        onHide: onAdminHide,
        onHighlight: onAdminHighlight,
      })
    )
  } else if (isAdmin || isAuditor) {
    columns.push(
      getAuditorActions({
        t,
        onHide: onAuditorHide,
        onHighlight: onAuditorHighlight,
      })
    )
  } else if (status.is(LotStatus.Draft)) {
    columns.push(getDraftActions({ t, onValidate, onDuplicate, onDelete }))
  } else if (status.is(LotStatus.ToFix)) {
    columns.push(getToFixActions({ t, onCorrect, onDelete }, entity))
  } else if (status.is(LotStatus.Inbox)) {
    columns.push(getInboxActions({ t, onAccept, onComment, onReject }))
  } else if (isProducer || isTrader) {
    columns.push(getDuplicateActions({ t, onDuplicate }))
  } else {
    columns.push(arrow)
  }

  const rows: Row<Transaction>[] = transactions.lots.map((tx) => ({
    value: tx,
    onClick: () => navigate(`${tx.id}`),
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
