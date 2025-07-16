import { useTranslation } from "react-i18next"
import { AgreementStatus } from "../../../double-counting/types"
import { BadgeProps, Badge } from "@codegouvfr/react-dsfr/Badge"

const statusToVariant: Record<AgreementStatus, BadgeProps["severity"]> = {
  [AgreementStatus.ACTIVE]: "success",
  [AgreementStatus.EXPIRES_SOON]: "warning",
  [AgreementStatus.EXPIRED]: "warning",
  [AgreementStatus.INCOMING]: "info",
}

const AgreementStatusTag = ({ status }: { status?: AgreementStatus }) => {
  const { t } = useTranslation()

  const statusLabels = {
    [AgreementStatus.ACTIVE]: t("En cours"),
    [AgreementStatus.EXPIRES_SOON]: t("À renouveler"),
    [AgreementStatus.EXPIRED]: t("Expiré"),
    [AgreementStatus.INCOMING]: t("À venir"),
  }

  if (!status) return null

  return (
    <Badge severity={statusToVariant[status]}>{statusLabels[status]}</Badge>
  )
}
export default AgreementStatusTag
