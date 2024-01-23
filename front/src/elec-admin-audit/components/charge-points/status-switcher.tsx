import Tabs from "common/components/tabs"
import { ElecAdminAuditSnapshot, ElecAdminAuditStatus } from "elec-admin-audit/types"
import { ElecAdminSnapshot } from "elec-admin/types"
import { ElecTransferCertificateStatus, ElecCPOSnapshot } from "elec/types-cpo"
import { useTranslation } from "react-i18next"

interface StatusSwitcherProps {
    status: ElecAdminAuditStatus
    snapshot: ElecAdminAuditSnapshot | undefined
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
                    label: t("En attente ({{count}})", { count: snapshot?.charge_points_applications_pending })
                },

                {
                    key: ElecAdminAuditStatus.History,
                    path: ElecAdminAuditStatus.History.toLowerCase(),
                    label: t("Historique ({{count}})", { count: snapshot?.charge_points_applications_history })
                },


            ]}
        />
    )
}
