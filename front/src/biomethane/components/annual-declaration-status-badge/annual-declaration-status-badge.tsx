import { AnnualDeclarationStatus } from "biomethane/types"
import { Badge, BadgeProps } from "@codegouvfr/react-dsfr/Badge"
import { getDeclarationStatusLabel } from "biomethane/utils"

export const AnnualDeclarationStatusBadge = ({
  status,
}: {
  status: AnnualDeclarationStatus
}) => {
  const severityMapping: Record<
    AnnualDeclarationStatus,
    BadgeProps["severity"]
  > = {
    [AnnualDeclarationStatus.IN_PROGRESS]: "info",
    [AnnualDeclarationStatus.DECLARED]: "success",
    [AnnualDeclarationStatus.OVERDUE]: "warning",
  }

  return (
    <Badge severity={severityMapping[status]}>
      {getDeclarationStatusLabel(status)}
    </Badge>
  )
}
