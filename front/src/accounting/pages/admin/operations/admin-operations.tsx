import { lazy } from "react"
import { useParams } from "react-router-dom"
import { useTranslation } from "react-i18next"
import { useSelectedEntity } from "common/providers/selected-entity-provider"
import { SectorTabs } from "accounting/types"
import { Notice } from "common/components/notice"

const OperationsBiofuels = lazy(
  () => import("accounting/pages/operations/biofuels")
)
const OperationsElec = lazy(() => import("accounting/pages/operations/elec"))

export const AdminOperations = () => {
  const { category } = useParams()
  const { t } = useTranslation()
  const { hasSelectedEntity } = useSelectedEntity()

  if (!hasSelectedEntity) {
    return (
      <Notice noColor variant="info">
        {t("Sélectionnez un redevable pour consulter ses opérations.")}
      </Notice>
    )
  }

  return (
    <>
      {category === SectorTabs.BIOFUELS && <OperationsBiofuels />}
      {category === SectorTabs.ELEC && <OperationsElec />}
    </>
  )
}
