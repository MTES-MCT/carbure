import { AnnualDeclarationStatus } from "biomethane/types"
import { Badge, BadgeProps } from "@codegouvfr/react-dsfr/Badge"
import { getDeclarationStatusLabel } from "biomethane/utils"

export const AnnualDeclarationStatusBadge = ({
  status,
  submissionDate,
}: {
  status: AnnualDeclarationStatus
  submissionDate?: string | null
}) => {
  const severityMapping: Record<
    AnnualDeclarationStatus,
    BadgeProps["severity"]
  > = {
    [AnnualDeclarationStatus.IN_PROGRESS]: "info",
    [AnnualDeclarationStatus.DECLARED]: "success",
    [AnnualDeclarationStatus.OVERDUE]: "warning",
    [AnnualDeclarationStatus.NOT_STARTED]: "error",
  }

  return (
    <Badge severity={severityMapping[status]}>
      {getDeclarationStatusLabel(status, submissionDate)}
    </Badge>
  )
}
