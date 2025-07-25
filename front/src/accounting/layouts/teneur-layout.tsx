import { Autocomplete } from "common/components/autocomplete2"
import { useState } from "react"
import { Content, Row } from "common/components/scaffold"
import { Select } from "common/components/selects2"
import { useTranslation } from "react-i18next"
import { Outlet } from "react-router-dom"
import useEntity from "common/hooks/entity"
import { normalizeEntityPreview } from "common/utils/normalizers"
import { EntityPreview } from "common/types"
import { findEligibleTiruertEntities } from "accounting/components/recipient-form/api"

// Type pour le contexte d'Outlet
export type TeneurOutletContext = {
  selectedEntityId: number | undefined
}

export const TeneurLayout = () => {
  const { t } = useTranslation()
  const entity = useEntity()
  const { isAdmin } = entity
  const isAdminOrExternal = isAdmin || entity.isExternal
  const [selectedEntity, setSelectedEntity] = useState<
    EntityPreview | undefined
  >(undefined)

  const outletContext: TeneurOutletContext = {
    selectedEntityId: selectedEntity?.id,
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

        {isAdminOrExternal && (
          <div style={{ flex: 0.7 }}>
            <Autocomplete
              placeholder={t("Rechercher un redevable")}
              getOptions={(query) =>
                findEligibleTiruertEntities(entity.id, query)
              }
              normalize={normalizeEntityPreview}
              value={selectedEntity}
              onChange={setSelectedEntity}
            />
          </div>
        )}
      </Row>
      <Content marginTop>
        <Outlet context={outletContext} />
      </Content>
    </>
  )
}
