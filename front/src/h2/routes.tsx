import { lazy } from "react"
import { Navigate, Route, Routes } from "react-router-dom"

const StationsPage = lazy(() => import("h2/pages/stations"))

export const H2Routes = () => {
  return (
    <Routes>
      <Route path="stations" element={<StationsPage />} />
      <Route path="*" element={<Navigate replace to="stations" />} />
    </Routes>
  )
}
