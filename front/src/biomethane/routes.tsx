import useEntity from "common/hooks/entity"
import { lazy } from "react"
import { Navigate, Outlet, Route, Routes } from "react-router-dom"
import { AnnualDeclarationLayout } from "./layouts/annual-declaration-layout"
import { ContractProductionUnitProvider } from "./providers/contract-production-unit"
import {
  AnnualDeclarationProvider,
  useAnnualDeclaration,
} from "./providers/annual-declaration"
import { useRoutes } from "common/hooks/routes"
import { ExternalAdminPages } from "common/types"

const Digestate = lazy(() => import("biomethane/pages/digestate"))
const Energy = lazy(() => import("biomethane/pages/energy"))
const SupplyPlan = lazy(() => import("biomethane/pages/supply-plan"))

const BiomethaneContractPage = lazy(() => import("biomethane/pages/contract"))
const BiomethaneInjectionPage = lazy(() => import("biomethane/pages/injection"))
const BiomethaneProductionPage = lazy(
  () => import("biomethane/pages/production")
)

type REDIRECTED_ROUTES = "digestate" | "energy" | "supply-plan"
/**
 * Composant de redirection qui utilise l'année de déclaration courante
 * récupérée depuis le backend via AnnualDeclarationProvider
 */
const RedirectToCurrentYear = ({ path }: { path: REDIRECTED_ROUTES }) => {
  const biomethaneRoutes = useRoutes().BIOMETHANE()
  const { currentAnnualDeclaration } = useAnnualDeclaration()
  const year = currentAnnualDeclaration?.year

  if (!year) return null

  return <Navigate to={`${biomethaneRoutes.ROOT}/${year}/${path}`} />
}

const RedirectToCurrentYearRoute = ({ path }: { path: REDIRECTED_ROUTES }) => (
  <AnnualDeclarationProvider>
    <RedirectToCurrentYear path={path} />
  </AnnualDeclarationProvider>
)

export const BiomethaneRoutes = () => {
  const { isBiomethaneProducer, hasAdminRight } = useEntity()

  if (hasAdminRight(ExternalAdminPages.DREAL)) return <BiomethaneAdminRoutes />

  if (!isBiomethaneProducer) return null

  return (
    <Routes>
      {/* Routes sans année qui redirigent vers l'année de déclaration courante */}
      <Route
        path="digestate"
        element={<RedirectToCurrentYearRoute path="digestate" />}
      />
      <Route
        path="energy"
        element={<RedirectToCurrentYearRoute path="energy" />}
      />
      <Route
        path="supply-plan"
        element={<RedirectToCurrentYearRoute path="supply-plan" />}
      />

      <Route
        path=":year"
        element={
          <ContractProductionUnitProvider>
            <AnnualDeclarationLayout />
          </ContractProductionUnitProvider>
        }
      >
        <Route index element={<Navigate replace to="digestate" />} />
        <Route path="digestate" element={<Digestate />} />
        <Route path="energy" element={<Energy />} />
        <Route path="supply-plan" element={<SupplyPlan />} />
      </Route>

      <Route
        path=""
        element={
          <AnnualDeclarationProvider>
            <RedirectToCurrentYear path="digestate" />
          </AnnualDeclarationProvider>
        }
      />
    </Routes>
  )
}

export const BiomethaneSettingsRoutes = () => {
  return (
    <Routes>
      <Route
        path=""
        element={
          <AnnualDeclarationProvider>
            <Outlet />
          </AnnualDeclarationProvider>
        }
      >
        <Route index element={<Navigate replace to="contract" />} />
        <Route path="contract" element={<BiomethaneContractPage />} />
        <Route path="production" element={<BiomethaneProductionPage />} />
        <Route path="injection" element={<BiomethaneInjectionPage />} />
      </Route>
    </Routes>
  )
}

export const BiomethaneAdminRoutes = () => {
  return (
    <Routes>
      <Route path="admin" element={<Outlet />}>
        <Route index element={<Navigate replace to="declarations" />} />
        <Route path="declarations" element={<div>Declarations</div>} />
      </Route>
    </Routes>
  )
}
