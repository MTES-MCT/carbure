import Tabs from "common/components/tabs"
import { ElecCPOProvisionCertificateStatus, ElecCPOSnapshot } from "elec/types"
import { useTranslation } from "react-i18next"

interface StatusSwitcherProps {
    status: ElecCPOProvisionCertificateStatus
    snapshot: ElecCPOSnapshot | undefined
    onSwitch: (status: ElecCPOProvisionCertificateStatus) => void
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
            onFocus={(status) => onSwitch(status as ElecCPOProvisionCertificateStatus)}
            tabs={[
                {
                    key: ElecCPOProvisionCertificateStatus.Available,
                    path: ElecCPOProvisionCertificateStatus.Available.toLowerCase(),
                    label: t("Disponible ({{count}})", { count: snapshot?.provision_cert_available })
                },
                {
                    key: ElecCPOProvisionCertificateStatus.History,
                    path: ElecCPOProvisionCertificateStatus.History.toLowerCase(),
                    label: t("Historique ({{ count }})", { count: snapshot?.provision_cert_history })
                },
            ]}
        />
    )
}
