import useEntity from "carbure/hooks/entity"
import HashRoute from "common/components/hash-route"
import NoResult from "common/components/no-result"
import Pagination from "common/components/pagination"
import { ActionBar, Bar } from "common/components/scaffold"
import { useQuery } from "common/hooks/async"
import {
  ElecAdminAuditFilter,
  ElecAdminAuditSnapshot,
  ElecAdminAuditStatus,
} from "elec-audit-admin/types"
import MeterReadingsApplicationsTable from "elec/components/meter-readings/table"
import { ElecMeterReadingsApplication } from "elec/types"
import { useLocation, useMatch } from "react-router-dom"
import * as api from "../../api"
import { StatusSwitcher } from "../status-switcher"
import { MeterReadingsApplicationDetailsDialog } from "./details"
import ElecAdminAuditFilters from "../list-filters"
import { useElectAdminAuditQuery } from "./list-query"
import { useElecAdminAuditMeterReadingsQueryParamsStore } from "./list-query-params-store"

type TransferListProps = {
  snapshot: ElecAdminAuditSnapshot
  year: number
}

const MeterReadingsApplicationsList = ({
  snapshot,
  year,
}: TransferListProps) => {
  const entity = useEntity()
  const status = useAutoStatus()
  const location = useLocation()

  const [state, actions] = useElecAdminAuditMeterReadingsQueryParamsStore(
    entity,
    year,
    status,
    snapshot
  )
  const query = useElectAdminAuditQuery(state)
  const meterReadingsApplicationsResponse = useQuery(
    api.getMeterReadingsApplications,
    {
      key: "audit-meter-readings-applications",
      params: [query],
    }
  )

  const showMeterReadingsApplicationDetails = (
    meterReadingApplication: ElecMeterReadingsApplication
  ) => {
    return {
      pathname: location.pathname,
      search: location.search,
      hash: `application/${meterReadingApplication.id}`,
    }
  }

  const downloadMeterReadingsApplication = (
    meterReadingApplication: ElecMeterReadingsApplication
  ) => {
    api.downloadMeterReadingsApplication(entity.id, meterReadingApplication.id)
  }

  // const meterReadingsApplicationsData = elecAdminMeterReadingsApplicationsList
  const meterReadingsApplicationsData =
    meterReadingsApplicationsResponse.result?.data.data

  const total = meterReadingsApplicationsData?.total ?? 0
  const count = meterReadingsApplicationsData?.returned ?? 0
  return (
    <>
      <Bar>
        <ElecAdminAuditFilters
          filters={FILTERS}
          selected={state.filters}
          onSelect={actions.setFilters}
          getFilterOptions={(filter) =>
            api.getElecAdminAuditMeterReadingsApplicationsFilters(filter, query)
          }
        />
      </Bar>

      <section>
        <ActionBar>
          <StatusSwitcher
            status={status}
            onSwitch={actions.setStatus}
            historyCount={snapshot.meter_readings_applications_history}
            pendingCount={snapshot.meter_readings_applications_pending}
            auditDoneCount={snapshot.charge_points_applications_audit_done}
            auditInProgressCount={snapshot.meter_readings_applications_audit_in_progress}
          />
        </ActionBar>

        {count > 0 && meterReadingsApplicationsData ? (
          <>
            <MeterReadingsApplicationsTable
              loading={meterReadingsApplicationsResponse.loading}
              applications={
                meterReadingsApplicationsData.meter_readings_applications
              }
              onDownloadMeterReadingsApplication={
                downloadMeterReadingsApplication
              }
              rowLink={showMeterReadingsApplicationDetails}
              displayCpo={true}
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
          <NoResult loading={meterReadingsApplicationsResponse.loading} />
        )}
      </section>

      <HashRoute
        path="application/:id"
        element={<MeterReadingsApplicationDetailsDialog />}
      />
    </>
  )
}
export default MeterReadingsApplicationsList

const FILTERS = [ElecAdminAuditFilter.Cpo, ElecAdminAuditFilter.Quarter]

export function useAutoStatus() {
  const matchStatus = useMatch(
    "/org/:entity/elec-admin-audit/:year/:view/:status/*"
  )
  const status =
    matchStatus?.params?.status?.toUpperCase() as ElecAdminAuditStatus
  return status ?? ElecAdminAuditStatus.Pending
}
