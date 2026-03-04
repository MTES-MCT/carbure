import { Row } from "common/components/scaffold"
import { Select } from "common/components/selects2"
import { useRoutes } from "common/hooks/routes"
import { useSelectedEntity } from "common/providers/selected-entity-provider"
import { useNavigate } from "react-router-dom"
import { BiomethaneProducer } from "../../types"
import { useAnnualDeclarationYearsAdmin } from "../../hooks/use-annual-declaration-years-admin"
import { useAnnualDeclaration } from "biomethane/providers/annual-declaration"
import { AnnualDeclarationIsOpenBadge } from "./annual-declaration-is-open-badge"
import { ToggleDeclarationButton } from "./toggle-declaration-button"
import useEntity from "common/hooks/entity"

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
  const entity = useEntity()
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

      <SelectYears key={selectedEntityId} />
      {/* Only display the open badge if the declaration exists */}
      {annualDeclaration && (
        <AnnualDeclarationIsOpenBadge
          isDeclarationOpen={annualDeclaration?.is_open ?? false}
        />
      )}
      {entity.canWrite() && <ToggleDeclarationButton />}
    </Row>
  )
}

// Use a separate component to set a key to the select to force a re-render when the selected entity changes
const SelectYears = () => {
  const years = useAnnualDeclarationYearsAdmin()
  return (
    <Select
      options={years.options}
      value={years.selected}
      onChange={years.setYear}
    />
  )
}
