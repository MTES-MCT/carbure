import React from "react"
import cl from "clsx"
import format from "date-fns/format"
import fr from "date-fns/locale/fr"

import { LotDetails, Transaction } from "common/types"
import { Box, Title } from "common/components"
import { hasDeadline } from "../helpers"

import styles from "./status.module.css"
import { EntitySelection } from "carbure/hooks/use-entity"

function getStatusText(
  tx: Transaction | undefined,
  entity?: EntitySelection,
  isStock: boolean = false
): string {
  if (!tx || tx.lot.status === "Draft") {
    return isStock ? "À envoyer" : "Brouillon"
  }

  const isClient = tx.carbure_client?.id === entity?.id

  if (tx.is_forwarded) {
    return "Transféré"
  }

  switch (tx.delivery_status) {
    case "N":
      return "En attente"
    case "A":
      return isStock ? "En stock" : "Accepté"
    case "R":
      return "Refusé"
    case "AC":
      return isClient ? "En correction" : "À corriger"
    case "AA":
      return "Corrigé"
  }
}

function getStatusClass(
  tx: Transaction | undefined,
  entity?: EntitySelection,
  isStock: boolean = false
): string {
  if (!tx || tx.lot.status === "Draft") {
    return isStock ? styles.statusWaiting : ""
  }

  if (tx.is_forwarded) {
    return styles.statusWaiting
  }

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
  stock?: boolean
  small?: boolean
  entity?: EntitySelection
  transaction: Transaction | undefined
}

const Status = ({ stock, small, transaction, entity }: StatusProps) => (
  <span
    className={cl(
      styles.status,
      small && styles.smallStatus,
      getStatusClass(transaction, entity, stock)
    )}
  >
    {getStatusText(transaction, entity, stock)}
  </span>
)

type StatusTitleProps = {
  stock?: boolean
  editable?: boolean
  details?: LotDetails | null
  entity?: EntitySelection
  children: React.ReactNode
}

export const StatusTitle = ({
  stock,
  editable,
  details,
  entity,
  children,
}: StatusTitleProps) => {
  const deadlineDate = details
    ? format(new Date(details.deadline), "d MMMM Y", { locale: fr })
    : null

  return (
    <Box row className={styles.statusTitle}>
      <Title>{children}</Title>

      <Status
        stock={stock}
        transaction={details?.transaction}
        entity={entity}
      />

      {details && hasDeadline(details.transaction, details.deadline) && (
        <span className={styles.transactionDeadline}>
          Ce lot doit être validé avant le <b>{deadlineDate}</b>
        </span>
      )}

      {/* {!editable && (
        <span className={styles.transactionEditable}>
          (Ce lot ne peut pas être modifié)
        </span>
      )} */}
    </Box>
  )
}

export default Status
