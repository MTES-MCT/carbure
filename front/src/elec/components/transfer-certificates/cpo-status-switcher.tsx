import Tabs from "common/components/tabs"
import { ElecTransferCertificateStatus, ElecCPOSnapshot } from "elec/types-cpo"
import { useTranslation } from "react-i18next"

interface StatusSwitcherProps {
  status: ElecTransferCertificateStatus
  snapshot: ElecCPOSnapshot | undefined
  onSwitch: (status: ElecTransferCertificateStatus) => void
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
      onFocus={(status) => onSwitch(status as ElecTransferCertificateStatus)}
      tabs={[
        {
          key: ElecTransferCertificateStatus.Pending,
          path: ElecTransferCertificateStatus.Pending.toLowerCase(),
          label: t("En attente ({{count}})", {
            count: snapshot?.transfer_certificates_pending,
          }),
        },

        {
          key: ElecTransferCertificateStatus.Accepted,
          path: ElecTransferCertificateStatus.Accepted.toLowerCase(),
          label: t("Acceptés ({{count}})", {
            count: snapshot?.transfer_certificates_accepted,
          }),
        },

        {
          key: ElecTransferCertificateStatus.Rejected,
          path: ElecTransferCertificateStatus.Rejected.toLowerCase(),
          label: t("Refusés ({{count}})", {
            count: snapshot?.transfer_certificates_rejected,
          }),
        },
      ]}
    />
  )
}
