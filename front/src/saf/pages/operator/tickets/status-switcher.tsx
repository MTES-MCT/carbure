import Tabs from "common/components/tabs"
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

  return (
    <Tabs
      keepSearch
      variant="switcher"
      focus={status}
      onFocus={(status) => onSwitch(status as SafTicketStatus)}
      tabs={displayedStatuses.map((status) => {
        return {
          key: status,
          path: status.toLowerCase(),
          label: getStatusLabel(status),
        }
      })}
    />
  )
}
