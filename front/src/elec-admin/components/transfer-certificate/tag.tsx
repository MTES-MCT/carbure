import { Tag, TagProps, TagVariant } from "common/components/tag"
import { ElecCPOTransferCertificateStatus } from "elec/types-cpo"
import { useTranslation } from "react-i18next"

export interface TransferCertificateTagProps extends TagProps {
  status: ElecCPOTransferCertificateStatus | undefined
}

export const TransferCertificateTag = ({
  status,
  ...props
}: TransferCertificateTagProps) => {
  const { t } = useTranslation()

  let label: string = ""
  let variant: TagVariant = "none"
  switch (status) {
    case ElecCPOTransferCertificateStatus.Accepted:
      variant = "success"
      label = t("Accepté")
      break
    case ElecCPOTransferCertificateStatus.Rejected:
      variant = "warning"
      label = t("Rejeté")
      break
    case ElecCPOTransferCertificateStatus.Pending:
      variant = "info"
      label = t("En attente")
      break
  }

  return (
    <Tag {...props} variant={variant}>
      {label}
    </Tag>
  )
}

export default TransferCertificateTag
