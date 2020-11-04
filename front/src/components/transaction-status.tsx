import React from "react"
import cl from "clsx"

import { Transaction } from "../services/types"
import styles from "./transaction-status.module.css"
import { Box, Title } from "./system"

function getStatusText(tx: Transaction | undefined): string {
  if (!tx || tx.lot.status === "Draft") {
    return "Brouillon"
  }

  switch (tx.delivery_status) {
    case "N":
      return "En attente"
    case "A":
      return "Accepté"
    case "R":
      return "Refusé"
    case "AC":
      return "À corriger"
    case "AA":
      return "Corrigé"
  }
}

function getStatusClass(tx: Transaction | undefined): string {
  if (!tx || tx.lot.status === "Draft") return ""

  switch (tx.delivery_status) {
    case "N":
      return styles.statusWaiting
    case "R":
      return styles.statusRejected
    case "AC":
      return styles.statusToFix
    case "A":
    case "AA":
      return styles.statusAccepted
  }
}

type StatusProps = {
  small?: boolean
  transaction: Transaction | undefined
}

const Status = ({ small, transaction }: StatusProps) => (
  <span
    className={cl(
      styles.status,
      small && styles.smallStatus,
      getStatusClass(transaction)
    )}
  >
    {getStatusText(transaction)}
  </span>
)

type StatusTitleProps = {
  editable?: boolean
  transaction?: Transaction
  children: React.ReactNode
}

export const StatusTitle = ({
  editable,
  transaction,
  children,
}: StatusTitleProps) => (
  <Box row className={styles.statusTitle}>
    <Title>{children}</Title>
    <Status transaction={transaction} />
    {!editable && (
      <span className={styles.transactionEditable}>
        (Ce lot ne peut pas être modifié)
      </span>
    )}
  </Box>
)

export default Status
