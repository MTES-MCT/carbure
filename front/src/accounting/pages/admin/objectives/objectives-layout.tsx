import { ObjectivesYearSelect } from "accounting/components/objectives-year-select"
import { Content, Row } from "common/components/scaffold"
import { useQuery } from "common/hooks/async"
import { useTranslation } from "react-i18next"
import { Outlet, useNavigate, useParams } from "react-router"
import useEntity from "common/hooks/entity"
import { EntityPreview } from "common/types"
import { findEligibleTiruertEntities } from "accounting/components/recipient-form/api"
import { TiruertLiableAutocomplete } from "common/molecules/tiruert-liable-autocomplete"
import { useRoutes } from "common/hooks/routes"
import { usePrivateNavigation } from "common/layouts/navigation"
import { BetaPage } from "common/molecules/beta-page"
import { useAnnualDeclarationTiruert } from "accounting/providers/annual-declaration-tiruert.provider"

const ADMIN_OBJECTIVES_URL_ROOT = "admin/objectives"

export const ObjectivesLayout = () => {
  const { t } = useTranslation()
  const entity = useEntity()
  const navigate = useNavigate()
  const { entityId } = useParams<{ entityId?: string }>()
  const { selectedYear } = useAnnualDeclarationTiruert()
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
    navigate(
      routes.ACCOUNTING.ADMIN.OBJECTIVES_YEAR(selectedYear, selectedEntity?.id)
    )
  }

  return (
    <>
      <Row style={{ columnGap: "40px", alignItems: "flex-end" }}>
        <div>
          <ObjectivesYearSelect urlRoot={ADMIN_OBJECTIVES_URL_ROOT} />
        </div>
        <div style={{ flex: 0.7 }}>
          <TiruertLiableAutocomplete
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
