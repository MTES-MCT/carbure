// import Tabs from "common/components/tabs"
import { ChatDeleteLine, CheckLine, DraftFill } from "common/components/icon"
import { Tabs } from "common/components/tabs2"
import { compact } from "common/utils/collection"
import { useTranslation } from "react-i18next"
import { SafOperatorSnapshot, SafQueryType, SafTicketStatus } from "saf/types"

interface StatusSwitcherProps {
  status: SafTicketStatus
  count?: SafOperatorSnapshot
  type: SafQueryType
  onSwitch: (status: SafTicketStatus) => void
}
export const SafStatusSwitcher = ({
  status,
  count,
  type,
  onSwitch,
}: StatusSwitcherProps) => {
  const { t } = useTranslation()

  const displayedStatuses = compact([
    SafTicketStatus.PENDING,
    type === "assigned" && SafTicketStatus.REJECTED,
    SafTicketStatus.ACCEPTED,
  ])

  const getStatusLabel = (status: SafTicketStatus) => {
    if (type === "assigned") {
      switch (status) {
        case SafTicketStatus.PENDING:
          return `${t("En attente")} (${count?.tickets_assigned_pending ?? 0})`
        case SafTicketStatus.REJECTED:
          return `${t("Refusés")} (${count?.tickets_assigned_rejected ?? 0})`
        case SafTicketStatus.ACCEPTED:
          return `${t("Acceptés")} (${count?.tickets_assigned_accepted ?? 0})`
      }
    } else if (type === "received") {
      switch (status) {
        case SafTicketStatus.PENDING:
          return `${t("En attente")} (${count?.tickets_received_pending ?? 0})`
        case SafTicketStatus.ACCEPTED:
          return `${t("Acceptés")} (${count?.tickets_received_accepted ?? 0})`
      }
    }
  }

  const getStatusIcon = (status: SafTicketStatus) => {
    switch (status) {
      case SafTicketStatus.PENDING:
        return DraftFill
      case SafTicketStatus.REJECTED:
        return ChatDeleteLine
      case SafTicketStatus.ACCEPTED:
        return CheckLine
    }
  }

  return (
    <Tabs
      focus={status}
      onFocus={(status) => onSwitch(status as SafTicketStatus)}
      tabs={displayedStatuses.map((status) => {
        return {
          key: status,
          label: getStatusLabel(status),
          icon: getStatusIcon(status),
          path: status.toLowerCase(),
        }
      })}
      keepSearch
    />
  )
}
