import useEntity from "carbure/hooks/entity"
import { Loader } from "common/components/icons"
import { Main } from "common/components/scaffold"
import Select from "common/components/select"
import Tabs from "common/components/tabs"
import { useQuery } from "common/hooks/async"
import useYears from "common/hooks/years"
import { useTranslation } from "react-i18next"
import { Navigate, Route, Routes } from "react-router-dom"
import * as api from "./api"
import ChargePointsApplicationsList from "./components/charge-points/list"
import MeterReadingsApplicationsList from "./components/meter-readings/list"
import { ElecAdminAuditSnapshot, ElecAdminAuditStatus } from "./types"


const defaultElecAdminAuditSnapshot: ElecAdminAuditSnapshot = {
  charge_points_applications: 0,
  charge_points_applications_pending: 0,
  charge_points_applications_audit_done: 0,
  charge_points_applications_audit_in_progress: 0,
  charge_points_applications_history: 0,
  meter_readings_applications: 0,
  meter_readings_applications_pending: 0,
  meter_readings_applications_audit_done: 0,
  meter_readings_applications_audit_in_progress: 0,
  meter_readings_applications_history: 0,
}


export const ElecAdminAudit = () => {
  const { t } = useTranslation()

  const entity = useEntity()

  const years = useYears("elec-admin-audit", api.getYears)
  const elecAdminAuditSnapshotResponse = useQuery(api.getSnapshot, {
    key: "elec-admin-audit-snapshot",
    params: [entity.id, years.selected],
  })

  const snapshot = elecAdminAuditSnapshotResponse.result?.data.data ?? defaultElecAdminAuditSnapshot

  return (

    <Main>
      <header>
        <section>
          <h1>{t("Audit des points de recharge")}</h1>

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
          <ElecAdminAuditTabs loading={elecAdminAuditSnapshotResponse.loading} snapshot={snapshot} />
        </section>

      </header>

      <Routes>
        <Route
          path="charge-points/*"
          element={
            <ChargePointsApplicationsList snapshot={snapshot} year={years.selected} />
          }
        />

        <Route
          path="meter-readings/*"
          element={
            <MeterReadingsApplicationsList snapshot={snapshot} year={years.selected} />
          }
        />
        <Route
          path="*"
          element={
            <Navigate
              replace
              to={`charge-points/${ElecAdminAuditStatus.Pending.toLocaleLowerCase()}`}
            />
          }
        />

      </Routes>

    </Main>


  )
}

export default ElecAdminAudit





interface ElecAdminAuditTabsProps {
  loading: boolean
  snapshot: ElecAdminAuditSnapshot
}


function ElecAdminAuditTabs({
  loading,
  snapshot
}: ElecAdminAuditTabsProps) {
  const { t } = useTranslation()

  return (<Tabs variant="main" tabs={[{
    key: "charge-points",
    path: "charge-points",
    label: <>
      <p style={{
        fontWeight: "normal"
      }}>
        {loading ? <Loader size={20} /> : snapshot?.charge_points_applications}
      </p>
      <strong>
        {t("Inscriptions")}
      </strong>
    </>
  }, {
    key: "meter-readings",
    path: "meter-readings",
    label: <>
      <p style={{
        fontWeight: "normal"
      }}>
        {loading ? <Loader size={20} /> : snapshot?.meter_readings_applications}
      </p>
      <strong>
        {t("Relevés")}
      </strong>
    </>
  }]} />);
}


