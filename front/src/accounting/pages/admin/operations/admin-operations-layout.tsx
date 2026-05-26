import { Autocomplete } from "common/components/autocomplete2"
import { Content, Row } from "common/components/scaffold"
import { Navigate, Outlet, useNavigate, useParams } from "react-router-dom"
import { useTranslation } from "react-i18next"
import { EntityPreview } from "common/types"
import { normalizeEntityPreview } from "common/utils/normalizers"
import { SelectedEntityProvider } from "common/providers/selected-entity-provider"
import { usePrivateNavigation } from "common/layouts/navigation"
import { BetaPage } from "common/molecules/beta-page"
import { AccountingSectorTabs } from "accounting/components/accounting-sector-tabs"
import { useRoutes } from "common/hooks/routes"
import { useEligibleTiruertEntities } from "accounting/hooks/use-eligible-tiruert-entities.hooks"

export const AdminOperationsLayout = () => {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const { selectedEntityId } = useParams<{
    selectedEntityId?: string
  }>()
  const routes = useRoutes()
  const parsedSelectedEntityId = selectedEntityId
    ? Number(selectedEntityId)
    : undefined

  const { entities, loading, isEntityMatchWithEntities, selectedEntity } =
    useEligibleTiruertEntities(parsedSelectedEntityId)

  usePrivateNavigation(<BetaPage title={t("Opérations")} />, "operations")

  const handleEntityChange = (
    nextSelectedEntity: EntityPreview | undefined
  ) => {
    if (!nextSelectedEntity?.id) return

    navigate(routes.ACCOUNTING.ADMIN.OPERATIONS_ENTITY(nextSelectedEntity.id))
  }

  if (
    selectedEntityId &&
    !loading &&
    !isEntityMatchWithEntities(selectedEntityId)
  ) {
    return <Navigate to={routes.ACCOUNTING.ADMIN.OPERATIONS} />
  }

  return (
    <SelectedEntityProvider selectedEntityId={parsedSelectedEntityId}>
      <Row style={{ columnGap: "40px", alignItems: "flex-end" }}>
        <div style={{ flex: 0.7 }}>
          <Autocomplete
            placeholder={t("Rechercher un redevable")}
            options={entities ?? []}
            normalize={normalizeEntityPreview}
            value={selectedEntity}
            onChange={handleEntityChange}
            loading={loading}
          />
        </div>
      </Row>
      {parsedSelectedEntityId && (
        <AccountingSectorTabs
          pathPrefix={routes.ACCOUNTING.ADMIN.OPERATIONS_ENTITY(
            parsedSelectedEntityId
          )}
        />
      )}
      <Content>
        <Outlet />
      </Content>
    </SelectedEntityProvider>
  )
}
