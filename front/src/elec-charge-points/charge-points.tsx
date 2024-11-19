import useEntity from "carbure/hooks/entity"
import { Main } from "common/components/scaffold"
import { useQuery } from "common/hooks/async"
import { Navigate, Route, Routes } from "react-router-dom"
import * as api from "./api"
import { ChargePointsSnapshot } from "./types"
import ElecMeterReadingsSettings from "./pages/meter-readings"
import ChargePointsList from "./pages/list"
import ChargePointsPending from "./pages/pending"

const defaultSnapshot: ChargePointsSnapshot = {
  charge_points: 0,
  charge_point_applications: 0,
  meter_reading_applications: 0,
  accepted: 0,
  audit_in_progress: 0,
  pending: 0,
}

const currentYear = new Date().getFullYear()

const ChargePoints = () => {
  const entity = useEntity()
  const snapshotResponse = useQuery(api.getChargePointsSnapshot, {
    key: "charge-points-snapshot",
    params: [entity.id],
  })

  const snapshot = snapshotResponse.result?.data.data ?? defaultSnapshot

  return (
    <Main>
      <Routes>
        <Route
          path="meter-readings"
          element={<ElecMeterReadingsSettings companyId={entity.id} />}
        />

        <Route
          path="list/*"
          element={<ChargePointsList year={currentYear} snapshot={snapshot} />}
        />

        <Route
          path="pending"
          element={<ChargePointsPending year={currentYear} />}
        />

        <Route path="*" element={<Navigate replace to="pending" />} />
      </Routes>
    </Main>
  )
}

export default ChargePoints
