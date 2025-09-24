import useEntity from "common/hooks/entity"
import { lazy } from "react"
import { Navigate, Route, Routes } from "react-router-dom"

const Digestate = lazy(() => import("biomethane/pages/digestate"))
const Energy = lazy(() => import("biomethane/pages/energy"))
const SupplyPlan = lazy(() => import("biomethane/pages/supply-plan"))
const currentYear = new Date().getFullYear()

export const BiomethaneRoutes = () => {
  const { isBiomethaneProducer } = useEntity()

  if (!isBiomethaneProducer) return null

  return (
    <Routes>
      <Route path="digestate/:year" element={<Digestate />} />
      <Route
        path="digestate"
        element={<Navigate replace to={`digestate/${currentYear}`} />}
      />
      <Route path="energy/:year" element={<Energy />} />
      <Route
        path="energy"
        element={<Navigate replace to={`energy/${currentYear}`} />}
      />
      <Route path="supply-plan/:year" element={<SupplyPlan />} />
      <Route
        path="supply-plan"
        element={<Navigate replace to={`supply-plan/${currentYear}`} />}
      />
      <Route
        path="digestate"
        element={<Navigate replace to={`digestate/${currentYear}`} />}
      />

      <Route
        path=""
        element={<Navigate replace to={`digestate/${currentYear}`} />}
      />
    </Routes>
  )
}
