import { MacSection } from "accounting/components/mac-section"
import { useAnnualDeclarationTiruert } from "accounting/providers/annual-declaration-tiruert.provider"
import { useTranslation } from "react-i18next"

type MacSectionAdminProps = {
  entityId: number
}

export const MacSectionAdmin = ({ entityId }: MacSectionAdminProps) => {
  const { t } = useTranslation()
  const { selectedYear } = useAnnualDeclarationTiruert()

  return (
    <MacSection
      title={t("Mises à consommation")}
      actionLabel={t("Voir ses MàC")}
      downloadLabel={t("Télécharger ses mises à consommation {{year}}", {
        year: selectedYear,
      })}
      readOnly
      entityId={entityId}
    />
  )
}
