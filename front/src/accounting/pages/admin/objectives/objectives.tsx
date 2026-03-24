import { Notice } from "common/components/notice"
import { LoaderOverlay } from "common/components/scaffold"
import { useTranslation } from "react-i18next"
import { useParams } from "react-router-dom"
import useEntity from "common/hooks/entity"
import { useQuery } from "common/hooks/async"
import {
  getAdminObjectivesEntity,
  getObjectives,
} from "accounting/pages/teneur/api"
import { ObjectivesContent } from "accounting/pages/teneur/components/objectives-content"

const YEAR = 2025

async function getAdminObjectives(
  entityId: number,
  year: number,
  selectedEntityId: number | undefined
) {
  if (selectedEntityId !== undefined) {
    return getAdminObjectivesEntity(entityId, year, selectedEntityId)
  }
  return getObjectives(entityId, year, true)
}

export const Objectives = () => {
  const entity = useEntity()
  const { entityId } = useParams<{ entityId?: string }>()
  const { t } = useTranslation()

  const selectedEntityId = entityId ? Number(entityId) : undefined

  const { result: objectivesData, loading } = useQuery(getAdminObjectives, {
    key: `admin-objectives-${entity.id}-${selectedEntityId ?? "consolidated"}`,
    params: [entity.id, YEAR, selectedEntityId],
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
      <ObjectivesContent objectivesData={objectivesData} readOnly />
    </>
  )
}
