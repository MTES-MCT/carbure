import { useAnnualDeclarationTiruert } from "accounting/providers/annual-declaration-tiruert.provider"
import { Notice } from "common/components/notice"
import { LoaderOverlay } from "common/components/scaffold"
import { useTranslation } from "react-i18next"
import { useParams } from "react-router-dom"
import useEntity from "common/hooks/entity"
import { useQuery } from "common/hooks/async"
import { getObjectives } from "accounting/pages/teneur/api"
import { ObjectivesContent } from "accounting/pages/teneur/components/objectives-content"
import { MacSection } from "accounting/pages/teneur/components/mac-section"

export const Objectives = () => {
  const entity = useEntity()
  const { entityId } = useParams<{ entityId?: string; year?: string }>()
  const { selectedYear } = useAnnualDeclarationTiruert()
  const { t } = useTranslation()

  const selectedEntityId = entityId ? Number(entityId) : undefined

  const { result: objectivesData, loading } = useQuery(getObjectives, {
    key: `admin-objectives-${entity.id}-${selectedEntityId ?? "consolidated"}-${selectedYear}`,
    params: [entity.id, selectedYear, selectedEntityId],
  })

  if (loading) {
    return <LoaderOverlay />
  }

  const topNotice = selectedEntityId ? (
    <Notice noColor variant="info">
      {t("Vous consultez les objectifs du redevable sélectionné.")}
    </Notice>
  ) : (
    <Notice noColor variant="info">
      {t("Sur cette page, vous avez accès aux objectifs consolidés.")}
      <br />
      {t(
        "Vous pouvez également sélectionner un redevable pour consulter ses objectifs."
      )}
    </Notice>
  )

  return (
    <>
      {topNotice}
      {selectedEntityId && <MacSection readOnly entityId={selectedEntityId} />}
      <ObjectivesContent objectivesData={objectivesData} readOnly />
    </>
  )
}
