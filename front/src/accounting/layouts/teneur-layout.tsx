import { Autocomplete } from "common/components/autocomplete2"
import { useState, useEffect } from "react"
import { Content, LoaderOverlay, Row } from "common/components/scaffold"
import { findEligibleTiruertEntities } from "accounting/components/recipient-to-depot-form/api"
import { Select } from "common/components/selects2"
import { useTranslation } from "react-i18next"
import { Outlet } from "react-router-dom"
import useEntity from "common/hooks/entity"
import { normalizeEntityPreview } from "common/utils/normalizers"
import { EntityPreview } from "common/types"
import { getAdminObjectivesEntity } from "accounting/pages/teneur/api"
import { Objectives } from "accounting/pages/teneur/types"

// Type pour le contexte d'Outlet
export type TeneurOutletContext = {
  objectives: Objectives | undefined
  loading: boolean
  selectedEntityId: number | undefined
}

export const TeneurLayout = () => {
  const { t } = useTranslation()
  const entity = useEntity()
  const { isAdmin } = entity
  const [selectedEntity, setSelectedEntity] = useState<
    EntityPreview | undefined
  >(undefined)
  const [objectives, setObjectives] = useState<Objectives | undefined>(
    undefined
  )
  const [loading, setLoading] = useState<boolean>(false)

  useEffect(() => {
    if (selectedEntity?.id) {
      setLoading(true)
      getAdminObjectivesEntity(entity.id, 2025, selectedEntity.id)
        .then((data) => {
          setObjectives(data)
        })
        .catch((error) => {
          console.error("Error fetching admin objectives:", error)
        })
        .finally(() => {
          setLoading(false)
        })
    }
  }, [selectedEntity, entity.id])

  const outletContext: TeneurOutletContext = {
    objectives,
    loading,
    selectedEntityId: selectedEntity?.id,
  }

  return (
    <>
      <Row style={{ columnGap: "40px" }}>
        <div>
          <Select
            options={[{ label: `${t("Année")} 2025`, value: 2025 }]}
            value={2025}
            disabled
          />
        </div>

        {isAdmin && (
          <div style={{ flex: 1 }}>
            <Autocomplete
              label={t("Sélectionnez un redevable")}
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
        {loading && <LoaderOverlay />}
        <Outlet context={outletContext} />
      </Content>
    </>
  )
}
