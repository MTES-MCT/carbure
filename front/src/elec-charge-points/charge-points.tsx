import useEntity from "carbure/hooks/entity"
import { Main } from "common/components/scaffold"
import Select from "common/components/select"
import { useQuery } from "common/hooks/async"
import useYears from "common/hooks/years"
import { useTranslation } from "react-i18next"
import { Navigate, Route, Routes } from "react-router-dom"
import * as api from "./api"
import { ChargePointsTabs } from "./charge-points-tabs"
import { ChargePointsSnapshot } from "./types"
import ElecMeterReadingsSettings from "elec/components/meter-readings/settings"
import ChargePointsList from "./pages/charge-points-list"
import ChargePointsPending from "./pages/charge-points-pending"

const defaultSnapshot: ChargePointsSnapshot = {
  charge_points: 0,
  charge_point_applications: 0,
  meter_reading_applications: 0,
  charge_points_accepted: 0,
  charge_points_audit_in_progress: 0,
  charge_points_pending: 0,
}

const ChargePoints = () => {
  const { t } = useTranslation()
  const entity = useEntity()
  const years = useYears("charge-points", api.getYears)
  const snapshotResponse = useQuery(api.getChargePointsSnapshot, {
    key: "charge-points-snapshot",
    params: [entity.id, years.selected],
  })

  const snapshot = snapshotResponse.result?.data.data ?? defaultSnapshot

  return (
    <Main>
      <header>
        <section>
          <h1>{t("Points de recharge")}</h1>

          <Select
            loading={years.loading}
            variant="inline"
            placeholder={t("Choisir une année")}
            value={years.selected}
            onChange={years.setYear}
            options={years.options}
            sort={(year) => -year.value}
          />
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
          path="list"
          element={<ChargePointsList year={years.selected} />}
        />

        <Route
          path="pending"
          element={<ChargePointsPending year={years.selected} />}
        />

        <Route path="*" element={<Navigate replace to="pending" />} />
      </Routes>
    </Main>
  )
}

export default ChargePoints
