import { Autocomplete } from "common/components/autocomplete2"
import { Content, Row } from "common/components/scaffold"
import { Select } from "common/components/selects2"
import { useQuery } from "common/hooks/async"
import { useTranslation } from "react-i18next"
import { Outlet, useNavigate, useParams } from "react-router-dom"
import useEntity from "common/hooks/entity"
import { EntityPreview } from "common/types"
import { normalizeEntityPreview } from "common/utils/normalizers"
import { findEligibleTiruertEntities } from "accounting/components/recipient-form/api"
import { useRoutes } from "common/hooks/routes"
import { usePrivateNavigation } from "common/layouts/navigation"
import { BetaPage } from "common/molecules/beta-page"

export const ObjectivesLayout = () => {
  const { t } = useTranslation()
  const entity = useEntity()
  const navigate = useNavigate()
  const { entityId } = useParams<{ entityId?: string }>()
  const routes = useRoutes()

  usePrivateNavigation(<BetaPage title={t("Objectifs annuels")} />, "teneur")

  const { result: entities } = useQuery(findEligibleTiruertEntities, {
    key: `objectives-eligible-entities-${entity.id}`,
    params: [entity.id, ""],
  })
  const selectedEntity: EntityPreview | undefined =
    entityId && entities
      ? entities.find((e) => e.id === Number(entityId))
      : undefined

  const handleEntityChange = (selectedEntity: EntityPreview | undefined) => {
    if (selectedEntity?.id) {
      navigate(routes.ACCOUNTING.ADMIN.OBJECTIVES_ENTITY(selectedEntity.id))
    }
  }

  return (
    <>
      <Row style={{ columnGap: "40px", alignItems: "flex-end" }}>
        <div>
          <Select
            options={[{ label: `${t("Année")} 2025`, value: 2025 }]}
            value={2025}
            disabled
          />
        </div>
        <div style={{ flex: 0.7 }}>
          <Autocomplete
            placeholder={t("Rechercher un redevable")}
            getOptions={(query) =>
              findEligibleTiruertEntities(entity.id, query)
            }
            normalize={normalizeEntityPreview}
            value={selectedEntity}
            onChange={handleEntityChange}
          />
        </div>
      </Row>
      <Content marginTop>
        <Outlet />
      </Content>
    </>
  )
}
