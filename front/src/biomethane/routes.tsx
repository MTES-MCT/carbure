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

const Digestate = lazy(() => import("biomethane/pages/digestate"))
const Energy = lazy(() => import("biomethane/pages/energy"))
const SupplyPlan = lazy(() => import("biomethane/pages/supply-plan"))

const BiomethaneContractPage = lazy(() => import("biomethane/pages/contract"))
const BiomethaneInjectionPage = lazy(() => import("biomethane/pages/injection"))
const BiomethaneProductionPage = lazy(
  () => import("biomethane/pages/production")
)

const currentYear = new Date().getFullYear()

/**
 * Composant de redirection qui utilise l'année de déclaration courante
 * récupérée depuis le backend via AnnualDeclarationProvider
 */
const RedirectToCurrentYear = ({ path }: { path: "digestate" | "energy" }) => {
  const biomethaneRoutes = useRoutes().BIOMETHANE()
  const { currentAnnualDeclaration } = useAnnualDeclaration()
  const year = currentAnnualDeclaration?.year

  if (!year) return null

  return <Navigate to={`${biomethaneRoutes.ROOT}/${year}/${path}`} />
}

export const BiomethaneRoutes = () => {
  const { isBiomethaneProducer } = useEntity()

  if (!isBiomethaneProducer) return null

  return (
    <Routes>
      {/* Routes sans année qui redirigent vers l'année de déclaration courante */}
      <Route
        path="digestate"
        element={
          <AnnualDeclarationProvider>
            <RedirectToCurrentYear path="digestate" />
          </AnnualDeclarationProvider>
        }
      />
      <Route
        path="energy"
        element={
          <AnnualDeclarationProvider>
            <RedirectToCurrentYear path="energy" />
          </AnnualDeclarationProvider>
        }
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
      </Route>
      <Route path="supply-plan/:year" element={<SupplyPlan />} />
      <Route
        path="supply-plan"
        element={<Navigate replace to={`supply-plan/${currentYear}`} />}
      />

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
