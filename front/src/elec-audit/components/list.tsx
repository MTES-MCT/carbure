import useEntity from "carbure/hooks/entity"
import HashRoute from "common/components/hash-route"
import NoResult from "common/components/no-result"
import Pagination from "common/components/pagination"
import { ActionBar, Bar } from "common/components/scaffold"
import { useQuery } from "common/hooks/async"
import { ElecAdminAuditSnapshot } from "elec-audit-admin/types"
import ChargePointsApplicationsTable from "elec/components/charge-points/table"
import { ElecAuditApplicationStatus, ElecChargePointsApplication } from "elec/types"
import { useTranslation } from "react-i18next"
import { To, useLocation, useMatch } from "react-router-dom"
import * as api from "elec-audit/api"
import { useElecAuditChargePointsQueryParamsStore } from "./list-query-params-store"
import { useElecAuditQuery } from "./list-query"
import ElecAuditFilters from "./list-filters"
import { ElecAuditFilter, ElecAuditSnapshot, ElecAuditStatus } from "elec-audit/types"
import { StatusSwitcher } from "./status-switcher"
import AuditChargePointsApplicationsTable from "./table"
import ChargingPointsApplicationDetailsDialog from "./details"


type TransferListProps = {
  snapshot: ElecAuditSnapshot
  year: number
}

const ChargePointsApplicationsList = ({ snapshot, year }: TransferListProps) => {

  const entity = useEntity()
  const status = useAutoStatus()
  const { t } = useTranslation()
  const location = useLocation()

  const [state, actions] = useElecAuditChargePointsQueryParamsStore(entity, year, status, snapshot)
  const query = useElecAuditQuery(state)
  const chargePointsApplicationsResponse = useQuery(api.getChargePointsApplications, {
    key: "audit-charge-points-applications",
    params: [query],
  })

  const showChargePointsApplicationDetails = (chargePointApplication: ElecChargePointsApplication): To => {
    if (chargePointApplication.status === ElecAuditApplicationStatus.AuditDone) return {}

    return {
      pathname: location.pathname,
      search: location.search,
      hash: `application/${chargePointApplication.id}`,
    }
  }

  const chargePointsApplicationsData = chargePointsApplicationsResponse.result?.data.data
  const total = chargePointsApplicationsData?.total ?? 0
  const count = chargePointsApplicationsData?.returned ?? 0
  return (
    <>

      <Bar>
        <ElecAuditFilters
          filters={FILTERS}
          selected={state.filters}
          onSelect={actions.setFilters}
          getFilterOptions={(filter) =>
            api.getElecAuditChargePointsApplicationsFilters(filter, query)
          }
        />
      </Bar>

      <section>

        <ActionBar>
          <StatusSwitcher
            status={status}
            onSwitch={actions.setStatus}
            auditDoneCount={snapshot.charge_points_applications_audit_done}
            auditInProgressCount={snapshot.charge_points_applications_audit_in_progress}
          />


        </ActionBar>

        {count > 0 && chargePointsApplicationsData ? (
          <>
            <AuditChargePointsApplicationsTable
              loading={chargePointsApplicationsResponse.loading}
              applications={chargePointsApplicationsData.charge_points_applications}
              rowLink={showChargePointsApplicationDetails}
            />

            {(state.limit || 0) < total && (
              <Pagination
                page={state.page}
                limit={state.limit}
                total={total}
                onPage={actions.setPage}
                onLimit={actions.setLimit}
              />
            )}
          </>
        ) : (
          <NoResult
            loading={chargePointsApplicationsResponse.loading}
          />
        )}
      </section >


      <HashRoute path="application/:id" element={<ChargingPointsApplicationDetailsDialog />} />
    </>
  )
}
export default ChargePointsApplicationsList


const FILTERS = [
  ElecAuditFilter.Cpo,
]


export function useAutoStatus() {
  const matchStatus = useMatch("/org/:entity/elec-audit/:year/:status/*")
  const status = matchStatus?.params?.status?.toUpperCase() as ElecAuditStatus
  return status ?? ElecAuditStatus.AuditInProgress
}
