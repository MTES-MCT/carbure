import { MacSection } from "accounting/components/mac-section"
import { useAnnualDeclarationTiruert } from "accounting/providers/annual-declaration-tiruert.provider"
import useEntity from "common/hooks/entity"
import { useTranslation } from "react-i18next"

export const MacSectionTeneur = () => {
  const { t } = useTranslation()
  const entity = useEntity()
  const { selectedYear, currentDeclarationYear = 0 } =
    useAnnualDeclarationTiruert()

  const isReadOnly = selectedYear < currentDeclarationYear

  return (
    <MacSection
      title={t("Mises à consommation")}
      actionLabel={isReadOnly ? t("Voir mes MàC") : t("Renseigner mes MàC")}
      downloadLabel={t("Télécharger mes mises à consommation {{year}}", {
        year: selectedYear,
      })}
      description={t(
        "L'assiette de vos objectifs sera calculée sur la base des mises à consommation de carburants fossiles que vous aurez renseignées, ainsi que d'un PCI théorique."
      )}
      readOnly={isReadOnly}
      actionDisabled={!entity.canWrite()}
    />
  )
}
