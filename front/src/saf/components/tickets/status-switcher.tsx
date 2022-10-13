import Tabs from "common/components/tabs"
import { useTranslation } from "react-i18next"
import { SafOperatorSnapshot, SafTicketStatus } from "saf/types"

interface StatusSwitcherProps {
  status: SafTicketStatus
  count: SafOperatorSnapshot | undefined
  onSwitch: (status: SafTicketStatus) => void
}
export const StatusSwitcher = ({
  status,
  count,
  onSwitch,
}: StatusSwitcherProps) => {
  const { t } = useTranslation()

  return (
    <Tabs
      keepSearch
      variant="switcher"
      focus={status}
      onFocus={(status) => onSwitch(status as SafTicketStatus)}
      tabs={[
        {
          key: SafTicketStatus.Pending,
          path: SafTicketStatus.Pending,
          label: `${t("En attente")} (${count?.tickets_pending ?? 0})`,
        },
        {
          key: SafTicketStatus.Rejected,
          path: SafTicketStatus.Rejected,
          label: `${t("Refusés")} (${count?.tickets_rejected ?? 0})`,
        },
        {
          key: SafTicketStatus.Accepted,
          path: SafTicketStatus.Accepted,
          label: `${t("Acceptés")} (${count?.tickets_accepted ?? 0})`,
        },
      ]}
    />
  )
}
