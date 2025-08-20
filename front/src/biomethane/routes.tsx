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
      <Route path=":year/digestate" element={<Digestate />} />

      <Route path=":year/energy" element={<div>energy page</div>} />

      <Route path=":year" element={<Navigate replace to="digestate" />} />

      <Route
        path=""
        element={<Navigate replace to={`${currentYear}/digestate`} />}
      />
    </Routes>
  )
}
