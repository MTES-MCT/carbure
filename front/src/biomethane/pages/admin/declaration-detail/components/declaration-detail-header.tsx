import { Row } from "common/components/scaffold"
import { Select } from "common/components/selects2"
import { useRoutes } from "common/hooks/routes"
import { useSelectedEntity } from "common/providers/selected-entity-provider"
import { useNavigate } from "react-router-dom"
import { BiomethaneProducer } from "../../types"
import { useAnnualDeclarationYearsAdmin } from "../hooks/use-annual-declaration-years-admin"
import { useAnnualDeclaration } from "biomethane/providers/annual-declaration"
import { AnnualDeclarationIsOpenBadge } from "./annual-declaration-is-open-badge"
import { ToggleDeclarationButton } from "./toggle-declaration-button"

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
  const years = useAnnualDeclarationYearsAdmin()
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
      <Select
        options={years.options}
        value={years.selected}
        onChange={years.setYear}
      />
      <AnnualDeclarationIsOpenBadge
        isDeclarationOpen={annualDeclaration?.is_open ?? false}
      />
      <ToggleDeclarationButton />
    </Row>
  )
}
