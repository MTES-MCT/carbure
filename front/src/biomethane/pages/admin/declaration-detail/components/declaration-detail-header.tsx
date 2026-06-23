import { Row } from "common/components/scaffold"
import { Select } from "common/components/selects2"
import { useRoutes } from "common/hooks/routes"
import { useSelectedEntity } from "common/providers/selected-entity-provider"
import { useNavigate } from "react-router-dom"
import { BiomethaneProducer } from "../../types"
import { useAnnualDeclaration } from "biomethane/providers/annual-declaration"
import { ToggleDeclarationButton } from "./toggle-declaration-button"
import { AnnualDeclarationStatusBadge } from "biomethane/components/annual-declaration-status-badge"
import { useBiomethanePermissions } from "biomethane/hooks/use-biomethane-permissions"
import { SelectYearsAdmin } from "../../components/select-years-admin"

interface DeclarationDetailHeaderProps {
  producers: BiomethaneProducer[]
}

const normalizeProducer = (producer: BiomethaneProducer) => {
  return {
    label: producer.name,
    value: producer.id,
  }
}

export const DeclarationDetailHeader = ({
  producers,
}: DeclarationDetailHeaderProps) => {
  const { selectedEntityId } = useSelectedEntity()
  const { canEditDeclaration } = useBiomethanePermissions()
  const { annualDeclaration } = useAnnualDeclaration()
  const navigate = useNavigate()
  const routes = useRoutes()

  return (
    <Row style={{ alignItems: "center" }} gap="md">
      <Select
        options={producers}
        normalize={normalizeProducer}
        value={selectedEntityId}
        onChange={(value) => {
          if (value) {
            navigate(routes.BIOMETHANE().ADMIN.DECLARATION_DETAIL(value).ROOT)
          }
        }}
      />

      <SelectYearsAdmin
        key={selectedEntityId}
        urlRoot={`biomethane/admin/declarations/${selectedEntityId}`}
      />

      {/* Only display the open badge if the declaration exists */}
      {annualDeclaration?.status && (
        <AnnualDeclarationStatusBadge status={annualDeclaration.status} />
      )}
      {canEditDeclaration && <ToggleDeclarationButton />}
    </Row>
  )
}
