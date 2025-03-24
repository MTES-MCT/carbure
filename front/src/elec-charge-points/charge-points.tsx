import useEntity from "common/hooks/entity"
import { Main } from "common/components/scaffold"
import { useQuery } from "common/hooks/async"
import { Navigate, Route, Routes } from "react-router-dom"
import * as api from "./api"
import { ChargePointsSnapshot } from "./types"
import ElecMeterReadingsSettings from "./pages/meter-readings"
import ChargePointsList from "./pages/list"
import ChargePointsApplications from "./pages/applications"

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

        <Route path="applications" element={<ChargePointsApplications />} />

        <Route path="*" element={<Navigate replace to="applications" />} />
      </Routes>
    </Main>
  )
}

export default ChargePoints
