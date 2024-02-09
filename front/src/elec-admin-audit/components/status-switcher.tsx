import Tabs from "common/components/tabs"
import { ElecAdminAuditStatus } from "elec-admin-audit/types"
import { useTranslation } from "react-i18next"

interface StatusSwitcherProps {
    status: ElecAdminAuditStatus
    pendingCount: number
    historyCount: number
    onSwitch: (status: ElecAdminAuditStatus) => void
}
export const StatusSwitcher = ({
    status,
    pendingCount,
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
                    label: t("En attente ({{count}})", { count: pendingCount })
                },

                {
                    key: ElecAdminAuditStatus.History,
                    path: ElecAdminAuditStatus.History.toLowerCase(),
                    label: t("Historique ({{count}})", { count: historyCount })
                },


            ]}
        />
    )
}
