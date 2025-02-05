import { Tag, TagProps, TagVariant } from "common/components/tag"
import { useTranslation } from "react-i18next"

export interface TransferCertificateTiruertTagProps extends TagProps {
  used_in_tiruert: boolean
}

export const TransferCertificateTiruertTag = ({
  used_in_tiruert,
  ...props
}: TransferCertificateTiruertTagProps) => {
  const { t } = useTranslation()

  let label = ""
  let variant: TagVariant = "none"
  if (used_in_tiruert) {
    variant = "success"
    label = t("Déclaré")
  } else {
    variant = "info"
    label = t("Non déclaré")
  }

  return (
    <Tag {...props} variant={variant}>
      {label}
    </Tag>
  )
}

export default TransferCertificateTiruertTag
