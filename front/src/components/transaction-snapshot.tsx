import React from "react"

import { Snapshot } from "../services/lots"
import { ApiState } from "../hooks/use-api"

import styles from "./transaction-snapshot.module.css"

import { Plus } from "./icons"
import { Title, Button, StatusButton } from "./system"

type TransactionSnapshotProps = {
  snapshot: ApiState<Snapshot>
  activeStatus: { [k: string]: boolean }
  toggleStatus: Function
}

const TransactionSnapshot = ({
  snapshot,
  activeStatus,
  toggleStatus,
}: TransactionSnapshotProps) => {
  if (!snapshot.data) return null

  return (
    <div className={styles.transactionSnapshot}>
      <div className={styles.topRow}>
        <Title>Transactions</Title>

        <Button type="primary">
          <Plus />
          Ajouter des lots
        </Button>
      </div>

      <div className={styles.buttonRow}>
        <StatusButton
          active={activeStatus.drafts}
          amount={snapshot.data.lots.drafts}
          label="Brouillons"
          onClick={() => toggleStatus("drafts")}
        />

        <StatusButton
          active={activeStatus.validated}
          amount={snapshot.data.lots.validated}
          label="Lots Envoyés"
          onClick={() => toggleStatus("validated")}
        />

        <StatusButton
          active={activeStatus.tofix}
          amount={snapshot.data.lots.tofix}
          label="Lots à Corriger"
          onClick={() => toggleStatus("tofix")}
        />

        <StatusButton
          active={activeStatus.accepted}
          amount={snapshot.data.lots.accepted}
          label="Lots Acceptés"
          onClick={() => toggleStatus("accepted")}
        />
      </div>
    </div>
  )
}

export default TransactionSnapshot
