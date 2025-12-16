import { Navigate, Route, Routes } from "react-router-dom"
import { Main } from "common/components/scaffold"
import Teneur from "./pages/teneur"
import OperationsBalancesLayout from "./layouts/operations-balances-layout"
import Operations from "./pages/operations"
import Balances from "./pages/balances"
import useEntity from "common/hooks/entity"
import { TeneurLayout } from "./layouts/teneur-layout"
import { useLastSectorVisited } from "./hooks/last-sector-visited"

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
        {(entity.is_tiruert_liable || isAdmin || allowAccounting) && (
          <Route element={<TeneurLayout />}>
            <Route path="teneur" element={<Navigate replace to="2025" />} />
            <Route path="teneur/:year" element={<Teneur />} />
          </Route>
        )}
        <Route path="*" element={<Navigate replace to="operations" />} />
      </Routes>
    </Main>
  )
}

export default MaterialAccounting
