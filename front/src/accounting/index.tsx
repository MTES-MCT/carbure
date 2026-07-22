import { Navigate, Route, Routes } from "react-router-dom"
import { Main } from "common/components/scaffold"
import Teneur from "./pages/teneur"
import OperationsBalancesLayout from "./layouts/operations-balances-layout"
import Operations from "./pages/operations"
import Balances from "./pages/balances"
import { TeneurLayout } from "./layouts/teneur-layout"
import { useLastSectorVisited } from "./hooks/last-sector-visited"
import { ObjectivesLayout } from "./pages/admin/objectives/objectives-layout"
import { Objectives } from "./pages/admin/objectives/objectives"
import { AdminOperationsLayout } from "./pages/admin/operations/admin-operations-layout"
import { AdminOperations } from "./pages/admin/operations/admin-operations"
import {
  AnnualDeclarationTiruertProvider,
  useAnnualDeclarationTiruert,
} from "./providers/annual-declaration-tiruert.provider"
import { useRoutes } from "common/hooks/routes"
import { SectorTabs } from "./types"
import { useAccountingPermissions } from "./hooks/use-accounting-permissions"

const MaterialAccounting = () => {
  const permissions = useAccountingPermissions()
  const { adminPermissions } = permissions
  const lastSector = useLastSectorVisited()

  return (
    <Main>
      <Routes>
        {permissions.canAccessOperations && (
          <Route element={<OperationsBalancesLayout />}>
            <Route path={`operations/:category`} element={<Operations />} />
            <Route
              path="operations"
              element={<Navigate replace to={lastSector} />}
            />

            {permissions.canAccessBalances && (
              <>
                <Route path="balances/:category" element={<Balances />} />
                <Route
                  path="balances"
                  element={<Navigate replace to={lastSector} />}
                />
              </>
            )}
          </Route>
        )}
        {permissions.canAccessTeneur && (
          <Route
            element={
              <AnnualDeclarationTiruertProvider>
                <TeneurLayout />
              </AnnualDeclarationTiruertProvider>
            }
          >
            <Route
              path="teneur"
              element={<RedirectToCurrentDeclarationYearRoute />}
            />
            <Route path="teneur/:year" element={<Teneur />} />
          </Route>
        )}
        {adminPermissions.canAccessAdmin && (
          <>
            {adminPermissions.canAccessObjectives && (
              <Route
                path="admin/objectives"
                element={
                  <AnnualDeclarationTiruertProvider>
                    <ObjectivesLayout />
                  </AnnualDeclarationTiruertProvider>
                }
              >
                <Route index element={<RedirectToObjectivesYearRoute />} />
                <Route path=":year" element={<Objectives />} />
                <Route path=":year/entity/:entityId" element={<Objectives />} />
              </Route>
            )}
            {adminPermissions.canAccessOperations && (
              <Route
                path="admin/operations"
                element={<AdminOperationsLayout />}
              >
                <Route index element={<AdminOperations />} />
                <Route
                  path=":selectedEntityId/:category"
                  element={<AdminOperations />}
                />
                <Route
                  path=":selectedEntityId"
                  element={<Navigate replace to={SectorTabs.BIOFUELS} />}
                />
              </Route>
            )}
          </>
        )}
        <Route path="*" element={<Navigate replace to="operations" />} />
      </Routes>
    </Main>
  )
}

const RedirectToObjectivesYearRoute = () => {
  const { currentDeclarationYear } = useAnnualDeclarationTiruert()
  const routes = useRoutes().ACCOUNTING
  const year = currentDeclarationYear ?? new Date().getFullYear()

  return <Navigate to={routes.ADMIN.OBJECTIVES_YEAR(year)} replace />
}

const RedirectToCurrentDeclarationYearRoute = () => {
  const { currentDeclarationYear } = useAnnualDeclarationTiruert()
  const routes = useRoutes().ACCOUNTING
  const year = currentDeclarationYear ?? new Date().getFullYear()

  // This case can't happen, but we log an error to be sure
  if (!currentDeclarationYear) {
    console.error("No current declaration year found")
  }

  return <Navigate to={routes.TENEUR.YEAR(year)} />
}
export default MaterialAccounting
