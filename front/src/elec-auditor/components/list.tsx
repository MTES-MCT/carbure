import useEntity from "carbure/hooks/entity"
import HashRoute from "common/components/hash-route"
import NoResult from "common/components/no-result"
import Pagination from "common/components/pagination"
import { ActionBar, Bar } from "common/components/scaffold"
import { useQuery } from "common/hooks/async"
import FilterMultiSelect from "common/molecules/filter-select"
import * as api from "elec-auditor/api"
import {
  ElecAuditorApplication,
  ElecAuditorApplicationsFilter,
  ElecAuditorApplicationsSnapshot,
  ElecAuditorApplicationsStatus,
} from "elec-auditor/types"
import { useTranslation } from "react-i18next"
import { To, useLocation, useMatch } from "react-router-dom"
import {
  useCBQueryBuilder,
  useCBQueryParamsStore,
} from "../../common/hooks/query-builder"
import ApplicationDetailsDialog from "./details"
import { StatusSwitcher } from "./status-switcher"
import ApplicationsTable from "./table"
import { usePageTitle } from "./page-title"

type TransferListProps = {
  snapshot: ElecAuditorApplicationsSnapshot
  year: number
}

const ElecApplicationList = ({ snapshot, year }: TransferListProps) => {
  const entity = useEntity()
  const status = useAutoStatus()
  const location = useLocation()
  const { t } = useTranslation()

  const [state, actions] = useCBQueryParamsStore(entity, year, status, snapshot)
  const query = useCBQueryBuilder(state)
  usePageTitle(state)
  const auditApplicationsResponse = useQuery(api.getApplications, {
    key: "elec-audit-applications",
    params: [query],
  })

  const showChargePointsApplicationDetails = (
    auditApplication: ElecAuditorApplication
  ): To => {
    if (auditApplication.status === ElecAuditorApplicationsStatus.AuditDone)
      return {}

    return {
      pathname: location.pathname,
      search: location.search,
      hash: `application/${auditApplication.id}`,
    }
  }

  const auditApplicationsData = auditApplicationsResponse.result?.data.data
  const total = auditApplicationsData?.total ?? 0
  const count = auditApplicationsData?.returned ?? 0

  const filterLabels = {
    [ElecAuditorApplicationsFilter.Cpo]: t("Aménageur"),
  }
  return (
    <>
      <Bar>
        <FilterMultiSelect
          filterLabels={filterLabels}
          selected={state.filters}
          onSelect={actions.setFilters}
          getFilterOptions={(filter) => api.getFilters(filter, query)}
        />
      </Bar>

      <section>
        <ActionBar>
          <StatusSwitcher
            status={status}
            onSwitch={actions.setStatus}
            auditDoneCount={snapshot.charge_points_applications_audit_done}
            auditInProgressCount={
              snapshot.charge_points_applications_audit_in_progress
            }
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
          <NoResult loading={auditApplicationsResponse.loading} />
        )}
      </section>

      <HashRoute
        path="application/:id"
        element={<ApplicationDetailsDialog />}
      />
    </>
  )
}
export default ElecApplicationList

export function useAutoStatus() {
  const matchStatus = useMatch("/org/:entity/elec-audit/:year/:status/*")
  const status =
    matchStatus?.params?.status?.toUpperCase() as ElecAuditorApplicationsStatus
  return status ?? ElecAuditorApplicationsStatus.AuditInProgress
}
