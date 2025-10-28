import { useAnnualDeclaration } from "biomethane/providers/annual-declaration"
import { AnnualDeclarationStatus } from "biomethane/types"
import { Notice } from "common/components/notice"
import { useTranslation } from "react-i18next"

export const AnnualDeclarationAlert = () => {
  const { t } = useTranslation()
  const { currentAnnualDeclaration, isInDeclarationPeriod } =
    useAnnualDeclaration()

  if (
    !isInDeclarationPeriod ||
    currentAnnualDeclaration?.status === AnnualDeclarationStatus.IN_PROGRESS
  )
    return null

  return (
    <Notice
      variant="warning"
      icon="ri-alert-line"
      title={t("Déclaration annuelle déjà transmise")}
    >
      {t(
        "En cas de modification de champs sur cette page, votre déclaration annuelle (digestat et énergie) devra être soumise à nouveau."
      )}
    </Notice>
  )
}
