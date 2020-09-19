import React from "react"

import styles from "./transaction-snapshot.module.css"
import { Plus } from "./icons"
import { Title, Button } from "./system"

const TransactionSnapshot = () => (
  <div className={styles.transactionSnapshot}>
    <div className={styles.topRow}>
      <Title>Transactions</Title>

      <Button type="primary">
        <Plus />
        Ajouter des lots
      </Button>
    </div>
  </div>
)

export default TransactionSnapshot
