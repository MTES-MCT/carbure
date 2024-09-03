import Tabs from "common/components/tabs"
import { compact } from "common/utils/collection"
import { ChargePointsSnapshot } from "elec-charge-points/types"
import { useMemo } from "react"
import { useTranslation } from "react-i18next"
import { ChargePointsStatus } from "./types"

interface StatusSwitcherProps {
  status: any
  snapshot: ChargePointsSnapshot
  onSwitch: (status: any) => void
}
export const StatusSwitcher = ({
  status,
  snapshot,
  onSwitch,
}: StatusSwitcherProps) => {
  const { t } = useTranslation()

  const displayedStatuses = useMemo(
    () => [
      {
        key: ChargePointsStatus.Pending,
        label: `${t("En attente")} (${snapshot.pending})`,
      },
      {
        key: ChargePointsStatus.AuditInProgress,
        label: `${t("En cours d'audit")} (${snapshot.audit_in_progress})`,
      },
      {
        key: ChargePointsStatus.Accepted,
        label: `${t("Accepté")} (${snapshot.accepted})`,
      },
    ],
    [t, snapshot]
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
