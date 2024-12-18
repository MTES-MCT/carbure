import { useTranslation } from "react-i18next"
import { AgreementStatus } from "../../../double-counting/types"
import Tag, { TagVariant } from "common/components/tag"

const statusToVariant: Record<AgreementStatus, TagVariant> = {
  [AgreementStatus.ACTIVE]: "info",
  [AgreementStatus.EXPIRES_SOON]: "warning",
  [AgreementStatus.EXPIRED]: "none",
  [AgreementStatus.INCOMING]: "success",
}

const AgreementStatusTag = ({
  big,
  status,
}: {
  big?: boolean
  status?: AgreementStatus
}) => {
  const { t } = useTranslation()

  const statusLabels = {
    [AgreementStatus.ACTIVE]: t("En cours"),
    [AgreementStatus.EXPIRES_SOON]: t("À renouveler"),
    [AgreementStatus.EXPIRED]: t("Expiré"),
    [AgreementStatus.INCOMING]: t("À venir"),
  }

  return (
    <Tag big={big} variant={!status ? "none" : statusToVariant[status]}>
      {!status ? "..." : statusLabels[status]}
    </Tag>
  )
}
export default AgreementStatusTag
