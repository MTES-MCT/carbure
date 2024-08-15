import useEntity from "carbure/hooks/entity"
import HashRoute from "common/components/hash-route"
import NoResult from "common/components/no-result"
import Pagination from "common/components/pagination"
import { ActionBar, Bar } from "common/components/scaffold"
import { useQuery } from "common/hooks/async"
import * as api from "elec-auditor/api"
import { ElecAuditorApplication, ElecAuditorApplicationsFilter, ElecAuditorApplicationsFilterSelection, ElecAuditorApplicationsSnapshot, ElecAuditorApplicationsStates, ElecAuditorApplicationsStatus } from "elec-auditor/types"
import { To, useLocation, useMatch } from "react-router-dom"
import ApplicationDetailsDialog from "./details"
import ApplicationsFilters from "./list-filters"
import { useQueryBuilder } from "../../common/hooks/query-builder"
import { useApplicationsQueryParamsStore } from "./list-query-params-store"
import { StatusSwitcher } from "./status-switcher"
import ApplicationsTable from "./table"


type TransferListProps = {
  snapshot: ElecAuditorApplicationsSnapshot
  year: number
}

const ElecApplicationList = ({ snapshot, year }: TransferListProps) => {

  const entity = useEntity()
  const status = useAutoStatus()
  const location = useLocation()

  const [state, actions] = useApplicationsQueryParamsStore(entity, year, status, snapshot)
  const query = useQueryBuilder(state);
  const auditApplicationsResponse = useQuery(api.getApplications, {
    key: "elec-audit-applications",
    params: [query],
  })

  const showChargePointsApplicationDetails = (auditApplication: ElecAuditorApplication): To => {
    if (auditApplication.status === ElecAuditorApplicationsStatus.AuditDone) return {}

    return {
      pathname: location.pathname,
      search: location.search,
      hash: `application/${auditApplication.id}`,
    }
  }

  const auditApplicationsData = auditApplicationsResponse.result?.data.data
  const total = auditApplicationsData?.total ?? 0
  const count = auditApplicationsData?.returned ?? 0
  return (
    <>

      <Bar>
        <ApplicationsFilters
          filters={FILTERS}
          selected={state.filters}
          onSelect={actions.setFilters}
          getFilterOptions={(filter) =>
            api.getFilters(filter, query)
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

        {count > 0 && auditApplicationsData ? (
          <>
            <ApplicationsTable
              loading={auditApplicationsResponse.loading}
              applications={auditApplicationsData.audit_applications}
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
            loading={auditApplicationsResponse.loading}
          />
        )}
      </section >


      <HashRoute path="application/:id" element={<ApplicationDetailsDialog />} />
    </>
  )
}
export default ElecApplicationList


const FILTERS = [
  ElecAuditorApplicationsFilter.Cpo,
]


export function useAutoStatus() {
  const matchStatus = useMatch("/org/:entity/elec-audit/:year/:status/*")
  const status = matchStatus?.params?.status?.toUpperCase() as ElecAuditorApplicationsStatus
  return status ?? ElecAuditorApplicationsStatus.AuditInProgress
}
