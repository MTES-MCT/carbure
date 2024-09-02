import Tabs from "common/components/tabs"
import { ElecAuditorApplicationsStatus } from "elec-auditor/types"
import { useTranslation } from "react-i18next"

interface StatusSwitcherProps {
    status: ElecAuditorApplicationsStatus
    auditDoneCount: number
    auditInProgressCount: number
    onSwitch: (status: ElecAuditorApplicationsStatus) => void
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
            onFocus={(status) => onSwitch(status as ElecAuditorApplicationsStatus)}
            tabs={[


                {
                    key: ElecAuditorApplicationsStatus.AuditInProgress,
                    path: ElecAuditorApplicationsStatus.AuditInProgress.toLowerCase(),
                    label: t("En cours d'audit ({{count}})", { count: auditInProgressCount })
                },

                {
                    key: ElecAuditorApplicationsStatus.AuditDone,
                    path: ElecAuditorApplicationsStatus.AuditDone.toLowerCase(),
                    label: t("Audit terminé ({{count}})", { count: auditDoneCount })
                },


            ]}
        />
    )
}
