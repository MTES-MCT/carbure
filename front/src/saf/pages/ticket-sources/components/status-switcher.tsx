import { useTranslation } from "react-i18next"
import { SafSnapshot } from "saf/types"
import { SafTicketSourceStatus } from "../../../types"
import { Tabs } from "common/components/tabs2"

interface StatusSwitcherProps {
  status: SafTicketSourceStatus
  count: SafSnapshot | undefined
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
          path: "../ticket-sources/available",
          label: `${t("Disponible")} (${count?.ticket_sources_available ?? 0})`,
          icon: "fr-icon-draft-line",
          iconActive: "fr-icon-draft-fill",
        },
        {
          key: SafTicketSourceStatus.HISTORY,
          path: "../ticket-sources/history",
          label: `${t("Historique")} (${count?.ticket_sources_history ?? 0})`,
          icon: "fr-icon-send-plane-line",
          iconActive: "fr-icon-send-plane-fill",
        },
      ]}
    />
  )
}
