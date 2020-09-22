import React from "react"

import { LotStatus, Snapshot } from "../services/lots"
import { ApiState } from "../hooks/use-api"

import styles from "./transaction-snapshot.module.css"

import { Plus } from "./icons"
import { Title, Button, StatusButton } from "./system"

const STATUS = [
  { key: LotStatus.Drafts, label: "Brouillons" },
  { key: LotStatus.Validated, label: "Lots Envoyés" },
  { key: LotStatus.ToFix, label: "Lots à Corriger" },
  { key: LotStatus.Accepted, label: "Lots Acceptés" },
]

type TransactionSnapshotProps = {
  snapshot: ApiState<Snapshot>
  activeStatus: { [k: string]: boolean }
  toggleStatus: Function
}

const TransactionSnapshot = ({
  snapshot,
  activeStatus,
  toggleStatus,
}: TransactionSnapshotProps) => (
  <div className={styles.transactionSnapshot}>
    <div className={styles.topRow}>
      <Title>Transactions</Title>

      <Button type="primary">
        <Plus />
        Ajouter des lots
      </Button>
    </div>

    <div className={styles.buttonRow}>
      {STATUS.map(({ key, label }) => (
        <StatusButton
          key={key}
          active={activeStatus[key]}
          amount={snapshot.data?.lots[key] ?? 0}
          label={label}
          onClick={() => toggleStatus(key)}
        />
      ))}
    </div>
  </div>
)

export default TransactionSnapshot
