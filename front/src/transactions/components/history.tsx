import { useTranslation } from "react-i18next"
import { DeliveryStatus, LotUpdate } from "common/types"
import { Edit } from "common/components/icons"
import Table, { Column } from "common/components/table"
import { Collapsible } from "common/components/alert"
import { formatDate } from "settings/components/common"
import { padding } from "./list-columns"
import styles from "./history.module.css"

const HistoryStatus = ({ update }: { update: LotUpdate }) => {
  const { t } = useTranslation()

  const statusLabels = {
    [DeliveryStatus.Pending]: t("En attente"),
    [DeliveryStatus.Accepted]: t("Accepté"),
    [DeliveryStatus.Rejected]: t("Refusé"),
    [DeliveryStatus.ToFix]: t("Correction"),
    [DeliveryStatus.Fixed]: t("Corrigé"),
    [DeliveryStatus.Frozen]: t("Déclaré"),
  }

  const before = update.value_before as DeliveryStatus
  const after = update.value_after as DeliveryStatus

  return (
    <div>
      {update.value_after && (
        <span style={{ marginRight: 12 }}>{statusLabels[after]}</span>
      )}
      <span style={{ fontWeight: "normal", textDecoration: "line-through" }}>
        {statusLabels[before]}
      </span>
    </div>
  )
}

const HistoryValue = ({ update }: { update: LotUpdate }) => {
  if (update.field === "status") {
    return <HistoryStatus update={update} />
  }

  return (
    <div>
      {update.value_after && (
        <span style={{ marginRight: 12 }}>{update.value_after}</span>
      )}
      <span style={{ fontWeight: "normal", textDecoration: "line-through" }}>
        {update.value_before}
      </span>
    </div>
  )
}

type TransactionHistoryProps = {
  history: LotUpdate[] | undefined
}

const TransactionHistory = ({ history = [] }: TransactionHistoryProps) => {
  const { t } = useTranslation()

  const columns: Column<LotUpdate>[] = [
    padding,
    {
      header: "Date",
      render: (u) => formatDate(u.datetime, true),
    },
    {
      header: "Champ modifié",
      render: (u) => u.label ?? u.field,
    },
    {
      header: "Valeur",
      render: (u) => <HistoryValue update={u} />,
    },
    {
      header: "Modifié par",
      render: (u) => u.modified_by,
    },
    padding,
  ]

  const rows = history
    .filter((h) => t(h.field, { ns: "fields" }) !== h.field) // ignore fields that have no translation
    .map((value) => ({
      value: { ...value, label: t(value.field, { ns: "fields" }) },
    }))

  return (
    <Collapsible
      icon={Edit}
      title={t("Historique des corrections")}
      className={styles.history}
    >
      <Table columns={columns} rows={rows} className={styles.historyTable} />
    </Collapsible>
  )
}

export default TransactionHistory
