import { useTranslation } from "react-i18next"
import { SafSnapshot } from "saf/types"
import { SafTicketSourceStatus } from "../../types"
import { Tabs } from "common/components/tabs2"
import { DraftFill, SendPlaneLine } from "common/components/icon"

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
          icon: DraftFill,
        },
        {
          key: SafTicketSourceStatus.HISTORY,
          path: "../ticket-sources/history",
          label: `${t("Historique")} (${count?.ticket_sources_history ?? 0})`,
          icon: SendPlaneLine,
        },
      ]}
    />
  )
}
