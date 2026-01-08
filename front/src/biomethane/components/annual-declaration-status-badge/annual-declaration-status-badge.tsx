import { AnnualDeclarationStatus } from "biomethane/types"
import { useTranslation } from "react-i18next"
import { Badge, BadgeProps } from "@codegouvfr/react-dsfr/Badge"

export const AnnualDeclarationStatusBadge = ({
  status,
}: {
  status: AnnualDeclarationStatus
}) => {
  const { t } = useTranslation()
  const severityMapping: Record<
    AnnualDeclarationStatus,
    BadgeProps["severity"]
  > = {
    [AnnualDeclarationStatus.IN_PROGRESS]: "info",
    [AnnualDeclarationStatus.DECLARED]: "success",
    [AnnualDeclarationStatus.OVERDUE]: "warning",
  }
  const labelMapping = {
    [AnnualDeclarationStatus.IN_PROGRESS]: t("Déclaration en cours"),
    [AnnualDeclarationStatus.DECLARED]: t("Déclaration transmise"),
    [AnnualDeclarationStatus.OVERDUE]: t("Déclaration en retard"),
  }

  return (
    <Badge severity={severityMapping[status]}>{labelMapping[status]}</Badge>
  )
}
