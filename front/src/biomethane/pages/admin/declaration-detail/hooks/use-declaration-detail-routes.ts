import { useRoutes } from "common/hooks/routes"
import { useSelectedEntity } from "common/providers/selected-entity-provider"

export const useDeclarationDetailRoutes = () => {
  const { selectedEntityId } = useSelectedEntity()
  const routes = useRoutes()

  if (!selectedEntityId) {
    throw new Error("Selected entity ID is required")
  }

  return routes.BIOMETHANE().ADMIN.DECLARATION_DETAIL(selectedEntityId)
}
