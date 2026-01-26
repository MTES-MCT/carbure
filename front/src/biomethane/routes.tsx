import useEntity from "common/hooks/entity"
import { lazy } from "react"
import { Navigate, Outlet, Route, Routes } from "react-router-dom"
import { AnnualDeclarationLayout } from "./layouts/annual-declaration-layout"
import { ContractProductionUnitProvider } from "./providers/contract-production-unit"
import {
  AnnualDeclarationProvider,
  useAnnualDeclaration,
  useAnnualDeclarationYear,
} from "./providers/annual-declaration"
import { useRoutes } from "common/hooks/routes"
import { ClosedDeclaration } from "biomethane/components/closed-declaration"
import { ExternalAdminPages } from "common/types"

const currentYear = new Date().getFullYear()

const BiomethaneAdminDeclarationDetailPage = lazy(
  () => import("biomethane/pages/admin/declaration-detail")
)
const BiomethaneAdminDeclarationsPage = lazy(
  () => import("biomethane/pages/admin/declarations")
)

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
  const { annualDeclaration } = useAnnualDeclaration()
  const yearParam = useAnnualDeclarationYear()

  // If there is no current annual declaration and no year param,
  // we are in the closed declaration period, so we redirect to the closed declaration page
  if (annualDeclaration === undefined && yearParam === undefined)
    return <Navigate to={`${biomethaneRoutes.ROOT}/closed-declaration`} />

  return (
    <Navigate
      to={`${biomethaneRoutes.ROOT}/${annualDeclaration?.year}/${path}`}
    />
  )
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

      <Route path="closed-declaration" element={<ClosedDeclaration />} />

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
        <Route
          path="declarations"
          element={<BiomethaneAdminDeclarationsPage />}
        />

        <Route
          path="declarations/:selectedEntityId/:year/*"
          element={<BiomethaneAdminDeclarationDetailPage />}
        >
          <Route index element={<Navigate replace to="digestate" />} />
          <Route path="digestate" element={<Digestate />} />
          <Route path="energy" element={<Energy />} />
          <Route path="supply-plan" element={<SupplyPlan />} />
          <Route path="contract" element={<BiomethaneContractPage />} />
        </Route>
        <Route
          path="declarations/:selectedEntityId"
          element={<Navigate replace to={`${currentYear}`} />}
        />
      </Route>
    </Routes>
  )
}
