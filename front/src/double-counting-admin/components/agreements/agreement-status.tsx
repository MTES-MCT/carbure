import { useTranslation } from "react-i18next"
import { AgreementStatus } from "../../../double-counting/types"
import Tag, { TagVariant } from "common/components/tag"

const statusToVariant: Record<AgreementStatus, TagVariant> = {
  [AgreementStatus.Active]: "info",
  [AgreementStatus.ExpiresSoon]: "warning",
  [AgreementStatus.Expired]: "none",
  [AgreementStatus.Incoming]: "success",
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
    [AgreementStatus.Active]: t("En cours"),
    [AgreementStatus.ExpiresSoon]: t("À renouveler"),
    [AgreementStatus.Expired]: t("Expiré"),
    [AgreementStatus.Incoming]: t("À venir"),
  }

  return (
    <Tag big={big} variant={!status ? "none" : statusToVariant[status]}>
      {!status ? "..." : statusLabels[status]}
    </Tag>
  )
}
export default AgreementStatusTag
