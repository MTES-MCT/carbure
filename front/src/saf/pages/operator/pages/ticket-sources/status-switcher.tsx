import { useTranslation } from "react-i18next"
import { SafOperatorSnapshot } from "saf/types"
import { SafTicketSourceStatus } from "../../types"
import { Tabs } from "common/components/tabs2"
interface StatusSwitcherProps {
  status: SafTicketSourceStatus
  count: SafOperatorSnapshot | undefined
  onSwitch: (status: SafTicketSourceStatus) => void
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
      focus={status}
      onFocus={(status) => onSwitch(status as SafTicketSourceStatus)}
      tabs={[
        {
          key: SafTicketSourceStatus.AVAILABLE,
          path: SafTicketSourceStatus.AVAILABLE.toLowerCase(),
          label: `${t("Disponible")} (${count?.ticket_sources_available ?? 0})`,
          icon: "ri-draft-fill",
        },
        {
          key: SafTicketSourceStatus.HISTORY,
          path: SafTicketSourceStatus.HISTORY.toLowerCase(),
          label: `${t("Historique")} (${count?.ticket_sources_history ?? 0})`,
          icon: "ri-send-plane-line",
        },
      ]}
    />
  )
}
