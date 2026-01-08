import { Row } from "common/components/scaffold"
import { Select } from "common/components/selects2"
import { useRoutes } from "common/hooks/routes"
import { useSelectedEntity } from "common/providers/selected-entity-provider"
import { EntityPreview } from "common/types"
import { useNavigate } from "react-router-dom"

interface DeclarationDetailHeaderProps {
  producers: EntityPreview[]
}

const normalizeProducer = (producer: EntityPreview) => {
  return {
    label: producer.name,
    value: producer.id,
  }
}

export const DeclarationDetailHeader = ({
  producers,
}: DeclarationDetailHeaderProps) => {
  const { selectedEntityId } = useSelectedEntity()
  const navigate = useNavigate()
  const routes = useRoutes()

  return (
    <Row style={{ justifyContent: "space-between", alignItems: "center" }}>
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
    </Row>
  )
}
