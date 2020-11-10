import React from "react"
import cl from "clsx"
import format from "date-fns/format"
import fr from "date-fns/locale/fr"

import { LotDetails, Transaction } from "../../services/types"
import styles from "./transaction-status.module.css"
import { Box, Title } from "../system"
import { hasDeadline } from "./transaction-table"

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
  details?: LotDetails | null
  children: React.ReactNode
}

export const StatusTitle = ({
  editable,
  details,
  children,
}: StatusTitleProps) => {
  const deadlineDate = details
    ? format(new Date(details.deadline), "d MMMM Y", { locale: fr })
    : null

  return (
    <Box row className={styles.statusTitle}>
      <Title>{children}</Title>
      <Status transaction={details?.transaction} />

      {details && hasDeadline(details.transaction, details.deadline) && (
        <span className={styles.transactionDeadline}>
          Ce lot doit être validé avant le <b>{deadlineDate}</b>
        </span>
      )}

      {!editable && (
        <span className={styles.transactionEditable}>
          (Ce lot ne peut pas être modifié)
        </span>
      )}
    </Box>
  )
}

export default Status
