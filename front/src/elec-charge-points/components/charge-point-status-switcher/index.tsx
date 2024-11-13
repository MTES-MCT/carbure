import Tabs from "common/components/tabs"
import { useStatusLabels } from "elec-charge-points/hooks/charge-point-status.hooks"
import {
  ChargePointsSnapshot,
  ChargePointStatus,
} from "elec-charge-points/types"
import { useMemo } from "react"

interface ChargePointStatusSwitcherProps {
  status: any
  snapshot: ChargePointsSnapshot
  onSwitch: (status: any) => void
}
export const ChargePointStatusSwitcher = ({
  status,
  snapshot,
  onSwitch,
}: ChargePointStatusSwitcherProps) => {
  const statuses = useStatusLabels()

  const displayedStatuses = useMemo(
    () => [
      {
        key: ChargePointStatus.Pending,
        label: `${statuses[ChargePointStatus.Pending]} (${snapshot.pending})`,
      },
      {
        key: ChargePointStatus.AuditInProgress,
        label: `${statuses[ChargePointStatus.AuditInProgress]} (${snapshot.audit_in_progress})`,
      },
      {
        key: ChargePointStatus.Accepted,
        label: `${statuses[ChargePointStatus.Accepted]} (${snapshot.accepted})`,
      },
    ],
    [snapshot, statuses]
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
