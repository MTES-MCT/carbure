import React from "react"

import { LotStatus, Snapshot } from "common/types"
import { ApiState } from "common/hooks/use-api"
import { StatusSelection } from "transactions/hooks/query/use-status"
import { YearSelection } from "transactions/hooks/query/use-year"

import { Title } from "common/components"
import { Button, StatusButton } from "common/components/button"
import Select from "common/components/select"
import { Alert } from "common/components/alert"

import styles from "./list-snapshot.module.css"
import { Rapport } from "common/components/icons"
import { LotDeclarator } from "transactions/hooks/actions/use-declare-lots"

const STATUS_ORDER = [
  LotStatus.Draft,
  LotStatus.Alert,
  LotStatus.Validated,
  LotStatus.Inbox,
  LotStatus.ToFix,
  LotStatus.Correction,
  LotStatus.Stock,
  LotStatus.Accepted,
  LotStatus.Weird,
  LotStatus.ToSend,
  LotStatus.Declaration,
]

const STATUS_LABEL = {
  [LotStatus.Draft]: { singular: "Brouillon", plural: "Brouillons" },
  [LotStatus.Validated]: { singular: "Lot envoyé", plural: "Lots envoyés" },
  [LotStatus.ToFix]: { singular: "Lot à corriger", plural: "Lots à corriger" },
  [LotStatus.Accepted]: { singular: "Lot accepté", plural: "Lots acceptés" },
  [LotStatus.Weird]: { singular: "Lot incohérent", plural: "Lots incohérents" },
  [LotStatus.Inbox]: { singular: "Lot reçu", plural: "Lots reçus" },
  [LotStatus.Stock]: { singular: "Lot en stock", plural: "Lots en stock" },
  [LotStatus.ToSend]: { singular: "Lot à envoyer", plural: "Lots à envoyer" },
  [LotStatus.Alert]: { singular: "Alerte", plural: "Alertes" },
  [LotStatus.Correction]: { singular: "Correction", plural: "Corrections" },
  [LotStatus.Declaration]: { singular: "Lot déclaré", plural: "Lots déclarés" },
}

export function mapStatus(
  statuses: { [key: string]: number } | undefined,
  placeholder: LotStatus[]
): [LotStatus, string, number][] {
  const statusList: [string, number][] =
    typeof statuses === "undefined"
      ? placeholder.map((s) => [s, 0])
      : Object.entries(statuses)

  statusList.sort(
    (a, b) =>
      STATUS_ORDER.indexOf(a[0] as LotStatus) -
      STATUS_ORDER.indexOf(b[0] as LotStatus)
  )

  return statusList.map(([key, amount = 0]) => {
    const status = key as LotStatus
    const labels = STATUS_LABEL[status]
    return [status, amount === 1 ? labels.singular : labels.plural, amount]
  })
}

type TransactionSnapshotProps = {
  placeholder: LotStatus[]
  snapshot: ApiState<Snapshot>
  status: StatusSelection
  year: YearSelection
  declarator: LotDeclarator | null
}

export const TransactionSnapshot = ({
  placeholder,
  snapshot,
  status,
  year,
  declarator,
}: TransactionSnapshotProps) => (
  <div className={styles.transactionSnapshot}>
    {snapshot.error && <Alert level="error">{snapshot.error}</Alert>}

    {!snapshot.error && (
      <React.Fragment>
        <div className={styles.transactionHeader}>
          <Title>Transactions</Title>

          <Select
            level="inline"
            className={styles.transactionYear}
            value={year.selected}
            placeholder={snapshot.loading ? "…" : "Choisir une année"}
            options={snapshot.data?.years ?? []}
            onChange={(value) => year.setYear(value as number)}
          />

          {declarator && (
            <Button
              icon={Rapport}
              level="primary"
              className={styles.transactionDeclaration}
              onClick={declarator.confirmDeclaration}
            >
              Voir ma déclaration
            </Button>
          )}
        </div>

        <div className={styles.transactionStatus}>
          {mapStatus(snapshot.data?.lots, placeholder).map(
            ([key, label, amount]) => (
              <StatusButton
                key={key}
                active={key === status.active}
                loading={snapshot.loading}
                amount={amount}
                label={label}
                onClick={() => status.setActive(key)}
              />
            )
          )}
        </div>
      </React.Fragment>
    )}
  </div>
)

export default TransactionSnapshot
