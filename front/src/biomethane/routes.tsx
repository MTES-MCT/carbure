import useEntity from "common/hooks/entity"
import { lazy } from "react"
import { Navigate, Route, Routes } from "react-router-dom"
import { BiomethanePageHeader } from "./layouts/page-header"

const Digestate = lazy(() => import("biomethane/pages/digestate"))
const Energy = lazy(() => import("biomethane/pages/energy"))
const SupplyPlan = lazy(() => import("biomethane/pages/supply-plan"))
const currentYear = new Date().getFullYear()

export const BiomethaneRoutes = () => {
  const { isBiomethaneProducer } = useEntity()

  if (!isBiomethaneProducer) return null

  return (
    <Routes>
      <Route path=":year" element={<BiomethanePageHeader />}>
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
        element={<Navigate replace to={`${currentYear}/digestate`} />}
      />
    </Routes>
  )
}
