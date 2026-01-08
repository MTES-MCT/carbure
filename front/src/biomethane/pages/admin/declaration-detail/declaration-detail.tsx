import { SelectedEntityProvider } from "common/providers/selected-entity-provider"
import { Navigate, Outlet, useParams } from "react-router-dom"
import { DeclarationDetailHeader } from "./components/declaration-detail-header"
import { useRoutes } from "common/hooks/routes"
import { useBiomethaneProducers } from "../hooks/use-biomethane-producers"
import { Content, LoaderOverlay, Main } from "common/components/scaffold"
import { useTranslation } from "react-i18next"
import { usePrivateNavigation } from "common/layouts/navigation"
import { DeclarationDetailTabs } from "./components/declaration-detail-tabs"

export const BiomethaneAdminDeclarationDetailPage = () => {
  const { t } = useTranslation()
  usePrivateNavigation(t("Déclarations par établissement - détail"))
  const { selectedEntityId } = useParams<{ selectedEntityId: string }>()
  const routes = useRoutes()
  const { isEntityMatchWithProducers, loading, producers } =
    useBiomethaneProducers()

  if (!selectedEntityId) {
    return null
  }

  if (loading) {
    return <LoaderOverlay />
  }

  if (!isEntityMatchWithProducers(selectedEntityId)) {
    return <Navigate to={routes.BIOMETHANE().ADMIN.DECLARATIONS} />
  }

  return (
    <SelectedEntityProvider selectedEntityId={Number(selectedEntityId)}>
      <Main>
        <DeclarationDetailHeader producers={producers ?? []} />
        <DeclarationDetailTabs />
        <Content>
          <Outlet />
        </Content>
      </Main>
    </SelectedEntityProvider>
  )
}
