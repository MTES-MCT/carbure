import Tabs from "common/components/tabs"
import { ElecAdminAuditStatus } from "elec-audit-admin/types"
import { ElecAuditStatus } from "elec-audit/types"
import { useTranslation } from "react-i18next"

interface StatusSwitcherProps {
  status: ElecAuditStatus
  auditDoneCount: number
  auditInProgressCount: number
  onSwitch: (status: ElecAuditStatus) => void
}
export const StatusSwitcher = ({
  status,
  auditInProgressCount,
  auditDoneCount,
  onSwitch,
}: StatusSwitcherProps) => {
  const { t } = useTranslation()

  return (
    <Tabs
      focus={status}
      variant="switcher"
      onFocus={(status) => onSwitch(status as ElecAuditStatus)}
      tabs={[
        {
          key: ElecAuditStatus.AuditInProgress,
          path: ElecAuditStatus.AuditInProgress.toLowerCase(),
          label: t("En cours d'audit ({{count}})", {
            count: auditInProgressCount,
          }),
        },

        {
          key: ElecAuditStatus.AuditDone,
          path: ElecAuditStatus.AuditDone.toLowerCase(),
          label: t("Audit terminé ({{count}})", { count: auditDoneCount }),
        },
      ]}
    />
  )
}
