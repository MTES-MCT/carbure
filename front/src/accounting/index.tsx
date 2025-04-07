import { Main } from "common/components/scaffold"

import { Navigate, Route, Routes } from "react-router-dom"

import Teneur from "./pages/teneur"
import OperationsBalancesLayout from "./layouts/operations-balances-layout"
import Operations from "./pages/operations"
import Balances from "./pages/balances"
import useEntity from "common/hooks/entity"
import { UserRole } from "common/types"
import { TeneurLayout } from "./layouts/teneur-layout"

const currentYear = new Date().getFullYear()

const MaterialAccounting = () => {
  const entity = useEntity()
  const canTransfer =
    entity.hasRights(UserRole.ReadWrite) || entity.hasRights(UserRole.Admin)

  return (
    <Main>
      <Routes>
        <Route element={<OperationsBalancesLayout />}>
          <Route path="operations" element={<Operations />} />
          {canTransfer && <Route path="balances" element={<Balances />} />}
        </Route>
        {entity.is_tiruert_liable && (
          <Route element={<TeneurLayout />}>
            <Route
              path="teneur"
              element={<Navigate replace to={`${currentYear}`} />}
            />
            <Route path="teneur/:year" element={<Teneur />} />
          </Route>
        )}
        <Route path="*" element={<Navigate replace to="operations" />} />
      </Routes>
    </Main>
  )
}

export default MaterialAccounting
