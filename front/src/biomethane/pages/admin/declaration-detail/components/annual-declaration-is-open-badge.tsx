import Badge from "@codegouvfr/react-dsfr/Badge"
import { useTranslation } from "react-i18next"

type AnnualDeclarationIsOpenBadgeProps = {
  isDeclarationOpen: boolean
}
export const AnnualDeclarationIsOpenBadge = ({
  isDeclarationOpen,
}: AnnualDeclarationIsOpenBadgeProps) => {
  const { t } = useTranslation()
  return (
    <Badge severity={isDeclarationOpen ? "success" : "warning"}>
      {isDeclarationOpen ? t("Déclaration ouverte") : t("Déclaration fermée")}
    </Badge>
  )
}
