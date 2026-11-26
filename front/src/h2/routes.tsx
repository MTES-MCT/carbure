import useEntity from "common/hooks/entity"
import { lazy } from "react"
import { Navigate, Outlet, Route, Routes } from "react-router"
import { useH2Permissions } from "./hooks/use-h2-permissions"

const currentYear = new Date().getFullYear()

const StationsPage = lazy(() => import("h2/pages/stations"))
const LotsPage = lazy(() => import("h2/pages/lots"))
const VolumesPage = lazy(() => import("h2/pages/volumes"))
const SentCertificatesPage = lazy(() => import("h2/pages/sent-certificates"))
const LiableVolumesPage = lazy(() => import("h2/pages/liable-volumes"))
const LiableCertificatesPage = lazy(
  () => import("h2/pages/liable-certificates")
)
const AdminLotsPage = lazy(() => import("h2/pages/admin/lots"))
const AdminCertificatesPage = lazy(() => import("h2/pages/admin/certificates"))

const H2AdminRoutes = () => {
  return (
    <Routes>
      <Route path="admin" element={<Outlet />}>
        <Route
          path="lots"
          element={<Navigate replace to={`${currentYear}`} />}
        />
        <Route path="lots/:year" element={<AdminLotsPage />} />
        <Route path="stations" element={<StationsPage />} />
        <Route
          path="certificates"
          element={<Navigate replace to={`${currentYear}`} />}
        />
        <Route
          path="certificates/:year/:tab?"
          element={<AdminCertificatesPage />}
        />
      </Route>
      <Route path="*" element={<Navigate replace to="../admin/lots" />} />
    </Routes>
  )
}

export const H2Routes = () => {
  const { isHRS, is_tiruert_liable } = useEntity()
  const { canAccessAdmin } = useH2Permissions()

  if (canAccessAdmin) return <H2AdminRoutes />

  if (!isHRS && !is_tiruert_liable) return null

  return (
    <Routes>
      {isHRS && (
        <>
          <Route path="stations" element={<StationsPage />} />
          <Route
            path="lots"
            element={<Navigate replace to={`${currentYear}`} />}
          />
          <Route path="lots/:year" element={<LotsPage />} />
          <Route
            path="volumes"
            element={<Navigate replace to={`${currentYear}`} />}
          />
          <Route path="volumes/:year/:tab?" element={<VolumesPage />} />
          <Route
            path="sent-certificates"
            element={<Navigate replace to={`${currentYear}`} />}
          />
          <Route
            path="sent-certificates/:year/:tab?"
            element={<SentCertificatesPage />}
          />
        </>
      )}
      {is_tiruert_liable && (
        <>
          <Route
            path="liable-volumes"
            element={<Navigate replace to={`${currentYear}`} />}
          />
          <Route
            path="liable-volumes/:year/:tab?"
            element={<LiableVolumesPage />}
          />
          <Route
            path="liable-certificates"
            element={<Navigate replace to={`${currentYear}`} />}
          />
          <Route
            path="liable-certificates/:year/:tab?"
            element={<LiableCertificatesPage />}
          />
        </>
      )}
      <Route
        path="*"
        element={
          <Navigate replace to={isHRS ? "../stations" : "../liable-volumes"} />
        }
      />
    </Routes>
  )
}
