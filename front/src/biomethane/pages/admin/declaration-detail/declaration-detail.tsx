import { SelectedEntityProvider } from "common/providers/selected-entity-provider"
import { Navigate, Outlet, useParams } from "react-router-dom"
import { DeclarationDetailHeader } from "./components/declaration-detail-header"
import { useRoutes } from "common/hooks/routes"
import { useBiomethaneProducers } from "../hooks/use-biomethane-producers"
import { Content, LoaderOverlay, Main } from "common/components/scaffold"
import { useTranslation } from "react-i18next"
import { usePrivateNavigation } from "common/layouts/navigation"
import { DeclarationDetailTabs } from "./components/declaration-detail-tabs"
import { AnnualDeclarationProvider } from "biomethane/providers/annual-declaration"
import { ContractProductionUnitProvider } from "biomethane/providers/contract-production-unit"

export const BiomethaneAdminDeclarationDetailPage = () => {
  const { t } = useTranslation()

  const { selectedEntityId } = useParams<{ selectedEntityId: string }>()
  const routes = useRoutes()
  const { setTitle } = usePrivateNavigation()
  const { isEntityMatchWithProducers, loading, producers } =
    useBiomethaneProducers({
      onSuccess: (data) => {
        if (selectedEntityId) {
          const selectedEntityName = data?.find(
            (producer) => producer.id === Number(selectedEntityId)
          )?.name
          setTitle(
            t("Déclaration - {{entityName}}", {
              entityName: selectedEntityName,
            })
          )
        }
      },
    })

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
      <AnnualDeclarationProvider>
        <ContractProductionUnitProvider allowEmpty>
          <Main>
            <DeclarationDetailHeader producers={producers ?? []} />
            <DeclarationDetailTabs />
            <Content>
              <Outlet />
            </Content>
          </Main>
        </ContractProductionUnitProvider>
      </AnnualDeclarationProvider>
    </SelectedEntityProvider>
  )
}
