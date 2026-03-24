import { Navigate, Route, Routes } from "react-router-dom"
import { Main } from "common/components/scaffold"
import Teneur from "./pages/teneur"
import OperationsBalancesLayout from "./layouts/operations-balances-layout"
import Operations from "./pages/operations"
import Balances from "./pages/balances"
import useEntity from "common/hooks/entity"
import { TeneurLayout } from "./layouts/teneur-layout"
import { useLastSectorVisited } from "./hooks/last-sector-visited"
import { ObjectivesLayout } from "./pages/admin/objectives/objectives-layout"
import { Objectives } from "./pages/admin/objectives/objectives"
import {
  AnnualDeclarationTiruertProvider,
  useAnnualDeclarationTiruert,
} from "./providers/annual-declaration-tiruert.provider"
import { useRoutes } from "common/hooks/routes"

const MaterialAccounting = () => {
  const entity = useEntity()
  const { isAdmin, isExternal } = entity
  const allowAccounting = isExternal && entity.hasAdminRight("TIRIB")

  const lastSector = useLastSectorVisited()

  return (
    <Main>
      <Routes>
        <Route element={<OperationsBalancesLayout />}>
          <Route path={`operations/:category`} element={<Operations />} />
          <Route
            path="operations"
            element={<Navigate replace to={lastSector} />}
          />

          <Route path="balances/:category" element={<Balances />} />
          <Route
            path="balances"
            element={<Navigate replace to={lastSector} />}
          />
        </Route>
        {entity.is_tiruert_liable && (
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
        {(isAdmin || allowAccounting) && (
          <Route path="admin/objectives" element={<ObjectivesLayout />}>
            <Route index element={<Objectives />} />
            <Route path=":entityId" element={<Objectives />} />
          </Route>
        )}
        <Route path="*" element={<Navigate replace to="operations" />} />
      </Routes>
    </Main>
  )
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
