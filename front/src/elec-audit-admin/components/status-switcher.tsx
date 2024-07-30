import Tabs from "common/components/tabs"
import { ElecAdminAuditStatus } from "elec-audit-admin/types"
import { useTranslation } from "react-i18next"

interface StatusSwitcherProps {
  status: ElecAdminAuditStatus
  pendingCount: number
  historyCount: number
  // auditDoneCount: number
  auditInProgressCount: number
  onSwitch: (status: ElecAdminAuditStatus) => void
}
export const StatusSwitcher = ({
  status,
  pendingCount,
  auditInProgressCount,
  // auditDoneCount,
  historyCount,
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
          label: t("En attente ({{count}})", { count: pendingCount }),
        },

        {
          key: ElecAdminAuditStatus.AuditInProgress,
          path: ElecAdminAuditStatus.AuditInProgress.toLowerCase(),
          label: t("En cours d'audit ({{count}})", {
            count: auditInProgressCount,
          }),
        },
        // {
        //     key: ElecAdminAuditStatus.AuditDone,
        //     path: ElecAdminAuditStatus.AuditDone.toLowerCase(),
        //     label: t("Audit réalisé ({{count}})", { count: auditDoneCount })
        // },
        {
          key: ElecAdminAuditStatus.History,
          path: ElecAdminAuditStatus.History.toLowerCase(),
          label: t("Historique ({{count}})", { count: historyCount }),
        },
      ]}
    />
  )
}
