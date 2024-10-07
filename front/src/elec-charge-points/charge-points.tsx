import useEntity from "carbure/hooks/entity"
import { Main } from "common/components/scaffold"
import { useQuery } from "common/hooks/async"
import { useTranslation } from "react-i18next"
import { Navigate, Route, Routes } from "react-router-dom"
import * as api from "./api"
import { ChargePointsTabs } from "./charge-points-tabs"
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
  const { t } = useTranslation()
  const entity = useEntity()
  const snapshotResponse = useQuery(api.getChargePointsSnapshot, {
    key: "charge-points-snapshot",
    params: [entity.id],
  })

  const snapshot = snapshotResponse.result?.data.data ?? defaultSnapshot

  return (
    <Main>
      <header>
        <section>
          <h1>{t("Points de recharge")}</h1>
        </section>

        <section>
          <ChargePointsTabs
            loading={snapshotResponse.loading}
            snapshot={snapshot}
          />
        </section>
      </header>

      <Routes>
        <Route
          path="meter-readings"
          element={
            <ElecMeterReadingsSettings companyId={entity.id} contentOnly />
          }
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
