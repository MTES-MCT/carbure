import React from "react"
import cl from "clsx"
import format from "date-fns/format"
import fr from "date-fns/locale/fr"
import { TFunction, Trans, useTranslation } from "react-i18next"

import {
  LotDetails,
  Transaction,
  DeliveryStatus,
  LotStatus,
} from "common/types"
import { Box, Title } from "common/components"
import { hasDeadline } from "../helpers"

import styles from "./status.module.css"
import { EntitySelection } from "carbure/hooks/use-entity"
import { formatDate } from "settings/components/common"

// extract the status name from the lot details
export function getStatus(
  transaction: Transaction,
  entityID: number
): LotStatus {
  const status = transaction.lot.status.toLowerCase()
  const delivery = transaction.delivery_status

  const isAuthor = transaction.lot.added_by?.id === entityID
  const isVendor = transaction.carbure_vendor?.id === entityID
  const isClient = transaction.carbure_client?.id === entityID

  if (status === "draft") {
    return LotStatus.Draft
  } else if (status === "validated") {
    if (delivery === "F") {
      return LotStatus.Declaration
    } else if (delivery === "A") {
      return LotStatus.Accepted
    }
    // PRODUCTEUR
    else if (isVendor || isAuthor) {
      if (["N", "AA"].includes(delivery)) {
        return LotStatus.Validated
      } else if (["AC", "R"].includes(delivery)) {
        return LotStatus.ToFix
      }
    }
    // OPERATEUR
    else if (isClient && ["N", "AA", "AC"].includes(delivery)) {
      return LotStatus.Inbox
    }
  }

  return LotStatus.Weird
}

function getStatusText(
  t: TFunction<"translation">,
  tx: Transaction | undefined,
  entity?: EntitySelection,
  isStock: boolean = false
): string {
  if (!tx || tx.lot.status === "Draft") {
    return isStock ? t("À envoyer") : t("Brouillon")
  }

  if (tx.is_forwarded) {
    return t("Transféré")
  }

  const isVendor = tx.carbure_vendor?.id === entity?.id
  const isOwner =
    tx.carbure_vendor === null && tx.lot.added_by?.id === entity?.id

  switch (tx.delivery_status) {
    case DeliveryStatus.Pending:
      return t("En attente")
    case DeliveryStatus.Accepted:
      return isStock ? t("En stock") : t("Accepté")
    case DeliveryStatus.Rejected:
      return t("Refusé")
    case DeliveryStatus.ToFix:
      return isVendor || isOwner ? t("À corriger") : t("En correction")
    case DeliveryStatus.Fixed:
      return t("Corrigé")
    case DeliveryStatus.Frozen:
      return t("Déclaré")
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

const Status = ({ stock, small, transaction, entity }: StatusProps) => {
  const { t } = useTranslation()

  return (
    <span
      className={cl(
        styles.status,
        small && styles.smallStatus,
        getStatusClass(transaction, entity, stock)
      )}
    >
      {getStatusText(t, transaction, entity, stock)}
    </span>
  )
}
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

      <AddedBy transaction={details?.transaction} />

      {details && hasDeadline(details.transaction, details.deadline) && (
        <span className={styles.transactionDeadline}>
          <Trans>
            Ce lot doit être validé avant le <b>{{ deadlineDate }}</b>
          </Trans>
        </span>
      )}

      {editable && (
        <span className={styles.transactionEditable}>
          <Trans>* Les champs marqués d'une étoile sont obligatoires</Trans>
        </span>
      )}
    </Box>
  )
}

const AddedBy = ({
  transaction: tx,
}: {
  transaction: Transaction | undefined
}) => {
  const entity = tx?.lot.added_by?.name
  const date = tx?.lot.added_time && formatDate(tx.lot.added_time)

  if (!entity || !date) return null

  return (
    <span className={styles.addedBy}>
      <Trans>
        par <b>{{ entity }}</b> le {{ date }}
      </Trans>
    </span>
  )
}

export default Status
