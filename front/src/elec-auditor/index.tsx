import useEntity from "carbure/hooks/entity"
import { Main } from "common/components/scaffold"
import Select from "common/components/select"
import { useQuery } from "common/hooks/async"
import useYears from "common/hooks/years"
import { useTranslation } from "react-i18next"
import * as api from "./api"
import ElecApplicationList from "./components/list"
import { ElecAuditorApplicationsSnapshot } from "./types"
import { usePrivateNavigation } from "common/layouts/navigation"

const defaultElecAdminAuditSnapshot: ElecAuditorApplicationsSnapshot = {
  charge_points_applications_audit_done: 0,
  charge_points_applications_audit_in_progress: 0,
}

export const ElecAudit = () => {
  const { t } = useTranslation()
  usePrivateNavigation(t("Points de recharge à auditer"))
  const entity = useEntity()
  const years = useYears("elec-audit", api.getYears)
  const elecAdminAuditSnapshotResponse = useQuery(api.getSnapshot, {
    key: "elec-audit-snapshot",
    params: [entity.id, years.selected],
  })

  const snapshot =
    elecAdminAuditSnapshotResponse.result?.data.data ??
    defaultElecAdminAuditSnapshot

  return (
    <Main>
      <header>
        <section>
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

      <ElecApplicationList snapshot={snapshot} year={years.selected} />
    </Main>
  )
}

export default ElecAudit
