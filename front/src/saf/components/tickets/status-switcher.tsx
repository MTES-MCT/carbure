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
          key: SafTicketStatus.Pending.toLowerCase(),
          path: SafTicketStatus.Pending.toLowerCase(),
          label: `${t("En attente")} (${count?.tickets_pending ?? 0})`,
        },
        {
          key: SafTicketStatus.Rejected.toLowerCase(),
          path: SafTicketStatus.Rejected.toLowerCase(),
          label: `${t("Refusés")} (${count?.tickets_rejected ?? 0})`,
        },
        {
          key: SafTicketStatus.Accepted.toLowerCase(),
          path: SafTicketStatus.Accepted.toLowerCase(),
          label: `${t("Acceptés")} (${count?.tickets_accepted ?? 0})`,
        },
      ]}
    />
  )
}
