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
      {/* SI on a une date ET que le statut est DECLARED ? */}
      {submissionDate && status === AnnualDeclarationStatus.DECLARED ? (

        /* ALORS on écrit notre texte à la mano avec la date formatée */
        `Déclaration transmise le ${new Date(submissionDate).toLocaleDateString("fr-FR")}`

      ) : (

        /* SINON on utilise l'ancien fonctionnement standard */
        getDeclarationStatusLabel(status)

      )}
    </Badge>
  )
}