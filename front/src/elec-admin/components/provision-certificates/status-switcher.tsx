import Tabs from "common/components/tabs"
import { ElecAdminProvisionCertificateStatus, ElecAdminSnapshot } from "elec-admin/types"
import { useTranslation } from "react-i18next"

interface StatusSwitcherProps {
    status: ElecAdminProvisionCertificateStatus
    snapshot: ElecAdminSnapshot | undefined
    onSwitch: (status: ElecAdminProvisionCertificateStatus) => void
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
            onFocus={(status) => onSwitch(status as ElecAdminProvisionCertificateStatus)}
            tabs={[
                {
                    key: ElecAdminProvisionCertificateStatus.Available,
                    path: ElecAdminProvisionCertificateStatus.Available.toLowerCase(),
                    label: t("Disponible ({{count}})", { count: snapshot?.provision_certificates })
                },
                {
                    key: ElecAdminProvisionCertificateStatus.History,
                    path: ElecAdminProvisionCertificateStatus.History.toLowerCase(),
                    label: t("Historique ({{ count }})", { count: snapshot?.transfer_certificates })
                },
            ]}
        />
    )
}
