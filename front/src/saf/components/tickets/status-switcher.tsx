import Tabs from "common/components/tabs"
import { compact } from "common/utils/collection"
import { useTranslation } from "react-i18next"
import { SafOperatorSnapshot, SafTicketStatus } from "saf/types"

interface StatusSwitcherProps {
  status: SafTicketStatus
  displayedStatuses: SafTicketStatus[]
  count?: SafOperatorSnapshot
  onSwitch: (status: SafTicketStatus) => void
}
export const StatusSwitcher = ({
  displayedStatuses,
  status,
  count,
  onSwitch,
}: StatusSwitcherProps) => {
  const { t } = useTranslation()

  const getStatusLabel = (status: SafTicketStatus) => {
    switch (status) {
      case SafTicketStatus.Pending:
        return `${t("En attente")} (${count?.tickets_pending ?? 0})`
      case SafTicketStatus.Rejected:
        return `${t("Refusés")} (${count?.tickets_rejected ?? 0})`
      case SafTicketStatus.Accepted:
        return `${t("Acceptés")} (${count?.tickets_accepted ?? 0})`
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
