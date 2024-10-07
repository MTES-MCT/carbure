import Tabs from "common/components/tabs"
import { ChargePointsSnapshot } from "elec-charge-points/types"
import { useMemo } from "react"
import { useStatusLabels } from "./index.hooks"
import { ChargePointStatus } from "./types"

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
