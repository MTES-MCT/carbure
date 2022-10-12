import Tabs from "common/components/tabs"
import { useTranslation } from "react-i18next"
import { SafOperatorSnapshot, SafTicketSourceStatus } from "saf/types"

interface StatusSwitcherProps {
  status: string
  count: SafOperatorSnapshot | undefined
  onSwitch: (status: string) => void
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
      onFocus={onSwitch}
      tabs={[
        {
          key: SafTicketSourceStatus.Available,
          path: `ticket-sources/${SafTicketSourceStatus.Available}`,
          label: `${t("Disponible")} (${count?.ticket_sources_available ?? 0})`,
        },
        {
          key: SafTicketSourceStatus.History,
          path: `ticket-sources/${SafTicketSourceStatus.History}`,
          label: `${t("Historique")} (${count?.ticket_sources_history ?? 0})`,
        },
      ]}
    />
  )
}
