import Tabs from "common/components/tabs"
import { compact } from "common/utils/collection"
import { useMemo } from "react"
import { useTranslation } from "react-i18next"
import { ChargePointsStatus } from "./types"

interface StatusSwitcherProps {
  status: any
  count?: any
  onSwitch: (status: any) => void
}
export const StatusSwitcher = ({
  status,
  count,
  onSwitch,
}: StatusSwitcherProps) => {
  const { t } = useTranslation()

  const displayedStatuses = useMemo(
    () => [
      {
        key: ChargePointsStatus.Pending,
        label: `${t("En attente")} (1000)`,
      },
      {
        key: ChargePointsStatus.AuditInProgress,
        label: `${t("En cours d'audit")} (1000)`,
      },
      {
        key: ChargePointsStatus.Accepted,
        label: `${t("Accepté")} (1000)`,
      },
    ],
    [t]
  )

  return (
    <Tabs
      keepSearch
      variant="switcher"
      focus={status}
      onFocus={(status) => onSwitch(status)}
      tabs={displayedStatuses.map((status) => {
        return {
          key: status.key,
          path: status.key.toLowerCase(),
          label: status.label,
        }
      })}
    />
  )
}
