import Tabs from "common/components/tabs"
import {
  ElecAdminAuditSnapshot,
  ElecAdminAuditStatus,
} from "elec-audit-admin/types"
import { useTranslation } from "react-i18next"

interface StatusSwitcherProps {
  status: ElecAdminAuditStatus
  snapshot: ElecAdminAuditSnapshot
  onSwitch: (status: ElecAdminAuditStatus) => void
}
export const StatusSwitcher = ({
  status,
  snapshot,
  onSwitch,
}: StatusSwitcherProps) => {
  const { t } = useTranslation()
  return (
    <Tabs
      focus={status}
      variant="switcher"
      onFocus={(status) => onSwitch(status as ElecAdminAuditStatus)}
      tabs={[
        {
          key: ElecAdminAuditStatus.Pending,
          path: ElecAdminAuditStatus.Pending.toLowerCase(),
          label: t("En attente ({{count}})", {
            count: snapshot.meter_readings_applications_pending,
          }),
        },

        {
          key: ElecAdminAuditStatus.AuditInProgress,
          path: ElecAdminAuditStatus.AuditInProgress.toLowerCase(),
          label: t("En cours d'audit ({{count}})", {
            count: snapshot.meter_readings_applications_audit_in_progress,
          }),
        },
        {
          key: ElecAdminAuditStatus.AuditDone,
          path: ElecAdminAuditStatus.AuditDone.toLowerCase(),
          label: t("Audit à valider ({{count}})", {
            count: snapshot.meter_readings_applications_audit_done,
          }),
        },
        {
          key: ElecAdminAuditStatus.History,
          path: ElecAdminAuditStatus.History.toLowerCase(),
          label: t("Historique ({{count}})", {
            count: snapshot.meter_readings_applications_history,
          }),
        },
      ]}
    />
  )
}
