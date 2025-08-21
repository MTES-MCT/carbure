import useEntity from "common/hooks/entity"
import { lazy } from "react"
import { Navigate, Route, Routes } from "react-router-dom"

const Digestate = lazy(() => import("biomethane/pages/digestate"))
const currentYear = new Date().getFullYear()

export const BiomethaneRoutes = () => {
  const { isBiomethaneProducer } = useEntity()

  if (!isBiomethaneProducer) return null

  return (
    <Routes>
      <Route path="digestate/:year" element={<Digestate />} />

      <Route path="energy/:year" element={<div>energy page</div>} />

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
