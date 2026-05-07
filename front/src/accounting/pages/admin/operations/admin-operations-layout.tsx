import { Autocomplete } from "common/components/autocomplete2"
import { Content, Row } from "common/components/scaffold"
import { Tabs } from "common/components/tabs2"
import { useState } from "react"
import { Outlet } from "react-router-dom"
import { useTranslation } from "react-i18next"
import useEntity from "common/hooks/entity"
import { EntityPreview } from "common/types"
import { normalizeEntityPreview } from "common/utils/normalizers"
import { findEligibleTiruertEntities } from "accounting/components/recipient-form/api"
import { SelectedEntityProvider } from "common/providers/selected-entity-provider"
import { usePrivateNavigation } from "common/layouts/navigation"
import { BetaPage } from "common/molecules/beta-page"
import { SectorTabs } from "accounting/types"

export const AdminOperationsLayout = () => {
  const { t } = useTranslation()
  const entity = useEntity()

  const [selectedEntity, setSelectedEntity] = useState<
    EntityPreview | undefined
  >(undefined)

  usePrivateNavigation(<BetaPage title={t("Opérations")} />, "operations")

  return (
    <SelectedEntityProvider selectedEntityId={selectedEntity?.id}>
      <Row style={{ columnGap: "40px", alignItems: "flex-end" }}>
        <div style={{ flex: 0.7 }}>
          <Autocomplete
            placeholder={t("Rechercher un redevable")}
            getOptions={(query) =>
              findEligibleTiruertEntities(entity.id, query)
            }
            normalize={normalizeEntityPreview}
            value={selectedEntity}
            onChange={(entity) => {
              if (entity) setSelectedEntity(entity)
            }}
          />
        </div>
      </Row>
      <Tabs
        tabs={[
          {
            key: SectorTabs.BIOFUELS,
            label: t("Biocarburants"),
            path: SectorTabs.BIOFUELS,
            icon: "fr-icon-gas-station-fill",
          },
          {
            key: SectorTabs.ELEC,
            label: t("Électricité"),
            path: SectorTabs.ELEC,
            icon: "fr-icon-charging-pile-2-fill",
          },
        ]}
      />
      <Content>
        <Outlet />
      </Content>
    </SelectedEntityProvider>
  )
}
