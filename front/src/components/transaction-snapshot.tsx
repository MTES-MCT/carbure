import React from "react"

import { ApiState } from "../hooks/helpers/use-api"
import { LotStatus, Snapshot, StockSnapshot } from "../services/types"
import { StatusSelection } from "../hooks/query/use-status"
import { YearSelection } from "../hooks/query/use-year"

import styles from "./transaction-snapshot.module.css"

import { Title, StatusButton, Box } from "./system"
import Select from "./system/select"
import { Alert } from "./system/alert"

const STATUS_ORDER = [
  LotStatus.Draft,
  LotStatus.Validated,
  LotStatus.Inbox,
  LotStatus.ToFix,
  LotStatus.Stock,
  LotStatus.Accepted,
  LotStatus.Weird,
]

const STATUS_LABEL = {
  [LotStatus.Draft]: { singular: "Brouillon", plural: "Brouillons" },
  [LotStatus.Validated]: { singular: "Lot envoyé", plural: "Lots envoyés" },
  [LotStatus.ToFix]: { singular: "Lot à corriger", plural: "Lots à corriger" },
  [LotStatus.Accepted]: { singular: "Lot accepté", plural: "Lots acceptés" },
  [LotStatus.Weird]: { singular: "Lot incohérent", plural: "Lots incohérents" },
  [LotStatus.Inbox]: { singular: "Lot reçu", plural: "Lots reçus" },
  [LotStatus.Stock]: { singular: "Lot en stock", plural: "Lots en stock" },
}

function mapStatus(
  statuses: {[key: string] : number}  | undefined
): [LotStatus, string, number][] {
  if (!statuses) return []

  const statusList = Object.entries(statuses)

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
  snapshot: ApiState<Snapshot>
  status: StatusSelection
  year: YearSelection
}

export const TransactionSnapshot = ({
  snapshot,
  status,
  year,
}: TransactionSnapshotProps) => (
  <div className={styles.transactionSnapshot}>
    {snapshot.error && <Alert level="error">{snapshot.error}</Alert>}

    {!snapshot.error && (
      <React.Fragment>
        <div className={styles.transactionHeader}>
          <Title>Transactions</Title>

          <Select
            level="primary"
            className={styles.transactionYear}
            value={year.selected}
            placeholder={snapshot.loading ? "…" : "Choisir une année"}
            options={snapshot.data?.years ?? []}
            onChange={(value) => year.setYear(value as number)}
          />
        </div>

        <div className={styles.transactionStatus}>
          {mapStatus(snapshot.data?.lots).map(([key, label, amount]) => (
            <StatusButton
              key={key}
              active={key === status.active}
              loading={snapshot.loading}
              amount={amount}
              label={label}
              onClick={() => status.setActive(key)}
            />
          ))}
        </div>
      </React.Fragment>
    )}
  </div>
)

type StockSnapshotProps = {
  snapshot: ApiState<StockSnapshot>
  status: StatusSelection
}

export const StocksSnapshot = ({snapshot, status} : StockSnapshotProps) => (
  <div className={styles.transactionSnapshot}>
    {snapshot.error && <Alert level="error">{snapshot.error}</Alert>}

    {!snapshot.error && (
      <React.Fragment>
        <div className={styles.transactionHeader}>
          <Title>Stock</Title>
        </div>

        <div className={styles.transactionStatus}>
          {mapStatus(snapshot.data?.lots).map(([key, label, amount]) => (
            <StatusButton
              key={key}
              active={key === status.active}
              loading={snapshot.loading}
              amount={amount}
              label={label}
              onClick={() => status.setActive(key)}
            />
          ))}
        </div>
      </React.Fragment>
    )}
  </div>
)

export default TransactionSnapshot
