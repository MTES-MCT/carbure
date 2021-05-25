import React from "react"
import cl from "clsx"
import format from "date-fns/format"
import fr from "date-fns/locale/fr"

import { LotDetails, Transaction, DeliveryStatus } from "common/types"
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
    case DeliveryStatus.Pending:
      return "En attente"
    case DeliveryStatus.Accepted:
      return isStock ? "En stock" : "Accepté"
    case DeliveryStatus.Rejected:
      return "Refusé"
    case DeliveryStatus.ToFix:
      return isClient ? "En correction" : "À corriger"
    case DeliveryStatus.Fixed:
      return "Corrigé"
    case DeliveryStatus.Frozen:
      return 'Déclaré'
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
    case DeliveryStatus.Pending:
      return styles.statusWaiting
    case DeliveryStatus.Rejected:
      return styles.statusRejected
    case DeliveryStatus.ToFix:
        return styles.statusToFix
    case DeliveryStatus.Fixed:
    case DeliveryStatus.Accepted:
    case DeliveryStatus.Frozen:
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
      <Status
        stock={stock}
        transaction={details?.transaction}
        entity={entity}
      />

      <Title>{children}</Title>

      {details && hasDeadline(details.transaction, details.deadline) && (
        <span className={styles.transactionDeadline}>
          Ce lot doit être validé avant le <b>{deadlineDate}</b>
        </span>
      )}

      {editable && (
        <span className={styles.transactionEditable}>
          * Les champs marqués d'une étoile sont obligatoires
        </span>
      )}
    </Box>
  )
}

export default Status
