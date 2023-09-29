import Tabs from "common/components/tabs"
import { ElecAdminSnapshot } from "elec-admin/types"
import { ElecCPOTransferCertificateStatus, ElecCPOSnapshot } from "elec/types-cpo"
import { useTranslation } from "react-i18next"

interface StatusSwitcherProps {
    status: ElecCPOTransferCertificateStatus
    snapshot: ElecAdminSnapshot | undefined
    onSwitch: (status: ElecCPOTransferCertificateStatus) => void
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
            onFocus={(status) => onSwitch(status as ElecCPOTransferCertificateStatus)}
            tabs={[
                {
                    key: ElecCPOTransferCertificateStatus.Pending,
                    path: ElecCPOTransferCertificateStatus.Pending.toLowerCase(),
                    label: t("En attente ({{count}})", { count: snapshot?.transfer_certificates_pending })
                },

                {
                    key: ElecCPOTransferCertificateStatus.Accepted,
                    path: ElecCPOTransferCertificateStatus.Accepted.toLowerCase(),
                    label: t("Acceptés ({{count}})", { count: snapshot?.transfer_certificates_accepted })
                },

                {
                    key: ElecCPOTransferCertificateStatus.Rejected,
                    path: ElecCPOTransferCertificateStatus.Rejected.toLowerCase(),
                    label: t("Refusés ({{count}})", { count: snapshot?.transfer_certificates_rejected })
                },
            ]}
        />
    )
}
