import useEntity from "common/hooks/entity"
import { lazy } from "react"
import { Navigate, Route, Routes } from "react-router-dom"
import { useH2Permissions } from "./hooks/use-h2-permissions"

const currentYear = new Date().getFullYear()

const StationsPage = lazy(() => import("h2/pages/stations"))
const LotsPage = lazy(() => import("h2/pages/lots"))
const CertificatesPage = lazy(() => import("h2/pages/certificates"))
const AdminLotsPage = lazy(() => import("h2/pages/admin/lots"))
const AdminCertificatesPage = lazy(() => import("h2/pages/admin/certificates"))

const H2AdminRoutes = () => {
  return (
    <Routes>
      <Route
        path="admin/lots"
        element={<Navigate replace to={`${currentYear}`} />}
      />
      <Route path="admin/lots/:year" element={<AdminLotsPage />} />
      <Route
        path="admin/certificates"
        element={<Navigate replace to={`${currentYear}`} />}
      />
      <Route
        path="admin/certificates/:year"
        element={<AdminCertificatesPage />}
      />
      <Route path="*" element={<Navigate replace to="admin/lots" />} />
    </Routes>
  )
}

export const H2Routes = () => {
  const { isHRS } = useEntity()
  const { canAccessAdmin } = useH2Permissions()

  if (canAccessAdmin) return <H2AdminRoutes />

  if (!isHRS) return null

  return (
    <Routes>
      <Route path="stations" element={<StationsPage />} />
      <Route path="lots" element={<Navigate replace to={`${currentYear}`} />} />
      <Route path="lots/:year" element={<LotsPage />} />
      <Route
        path="certificates"
        element={<Navigate replace to={`${currentYear}`} />}
      />
      <Route path="certificates/:year" element={<CertificatesPage />} />
      <Route path="*" element={<Navigate replace to="stations" />} />
    </Routes>
  )
}
