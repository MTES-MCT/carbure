import useEntity from "carbure/hooks/entity"
import HashRoute from "common/components/hash-route"
import NoResult from "common/components/no-result"
import Pagination from "common/components/pagination"
import { ActionBar, Bar } from "common/components/scaffold"
import { useQuery } from "common/hooks/async"
import {
  useCBQueryBuilder,
  useCBQueryParamsStore,
} from "common/hooks/query-builder"
import {
  ElecAdminAuditFilter,
  ElecAdminAuditSnapshot,
  ElecAdminAuditStatus,
} from "elec-audit-admin/types"
import MeterReadingsApplicationsTable from "elec/components/meter-readings/table"
import { ElecMeterReadingsApplication } from "elec/types"
import { useTranslation } from "react-i18next"
import { useLocation, useMatch } from "react-router-dom"
import FilterMultiSelect from "../../../common/molecules/filter-select"
import * as api from "../../api"
import { StatusSwitcher } from "./status-switcher"
import { MeterReadingsApplicationDetailsDialog } from "./details"
import { usePageTitle } from "./page-title"

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
  const { t } = useTranslation()

  const [state, actions] = useCBQueryParamsStore(entity, year, status, snapshot)
  usePageTitle(state)
  const query = useCBQueryBuilder(state)

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

  const meterReadingsApplicationsData =
    meterReadingsApplicationsResponse.result?.data.data

  const total = meterReadingsApplicationsData?.total ?? 0
  const count = meterReadingsApplicationsData?.returned ?? 0

  const filterLabels = {
    [ElecAdminAuditFilter.Cpo]: t("Aménageur"),
    [ElecAdminAuditFilter.Quarter]: t("Trimestre"),
  }

  return (
    <>
      <Bar>
        <FilterMultiSelect
          filterLabels={filterLabels}
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
            snapshot={snapshot}
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

// const FILTERS = [ElecAdminAuditFilter.Cpo, ElecAdminAuditFilter.Quarter]

export function useAutoStatus() {
  const matchStatus = useMatch(
    "/org/:entity/elec-admin-audit/:year/:view/:status/*"
  )
  const status =
    matchStatus?.params?.status?.toUpperCase() as ElecAdminAuditStatus
  return status ?? ElecAdminAuditStatus.Pending
}
