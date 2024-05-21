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
import ChargePointsApplicationsList from "./components/list"
import { ElecAuditSnapshot } from "./types"


const defaultElecAdminAuditSnapshot: ElecAuditSnapshot = {
  charge_points_applications_audit_done: 0,
  charge_points_applications_audit_in_progress: 0,
}


export const ElecAudit = () => {
  const { t } = useTranslation()

  const entity = useEntity()
  const years = useYears("elec-audit", api.getYears)
  const elecAdminAuditSnapshotResponse = useQuery(api.getSnapshot, {
    key: "elec-audit-snapshot",
    params: [entity.id, years.selected],
  })

  const snapshot = elecAdminAuditSnapshotResponse.result?.data.data ?? defaultElecAdminAuditSnapshot

  return (

    <Main>
      <header>
        <section>
          <h1>{t("Points de recharge à auditer")}</h1>

          <Select
            loading={years.loading}
            variant="inline"
            placeholder={t("Année")}
            value={years.selected}
            onChange={years.setYear}
            options={years.options}
            sort={(year) => -year.value}
          />
        </section>


      </header>

      <ChargePointsApplicationsList snapshot={snapshot} year={years.selected} />

    </Main>


  )
}

export default ElecAudit



