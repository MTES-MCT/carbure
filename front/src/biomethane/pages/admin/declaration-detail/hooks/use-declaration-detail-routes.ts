import { useAnnualDeclarationYear } from "biomethane/providers/annual-declaration"
import { useRoutes } from "common/hooks/routes"
import { useSelectedEntity } from "common/providers/selected-entity-provider"

export const useDeclarationDetailRoutes = () => {
  const { selectedEntityId } = useSelectedEntity()
  const routes = useRoutes()
  const selectedYear = useAnnualDeclarationYear()

  if (!selectedEntityId) {
    throw new Error("Selected entity ID is required")
  }

  return routes
    .BIOMETHANE(selectedYear)
    .ADMIN.DECLARATION_DETAIL(selectedEntityId)
}
