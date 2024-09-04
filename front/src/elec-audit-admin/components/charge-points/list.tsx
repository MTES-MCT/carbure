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
import * as api from "elec-admin/api"
import {
  ElecAdminAuditFilter,
  ElecAdminAuditSnapshot,
  ElecAdminAuditStatus,
} from "elec-audit-admin/types"
import ChargePointsApplicationsTable from "elec/components/charge-points/table"
import { ElecChargePointsApplication } from "elec/types"
import { useTranslation } from "react-i18next"
import { useLocation, useMatch } from "react-router-dom"
import * as apiAudit from "../../api"
import FilterMultiSelect from "../../../common/molecules/filter-select"
import ChargePointsApplicationDetailsDialog from "./details"
import { usePageTitle } from "./page-title"
import { StatusSwitcher } from "./status-switcher"

type TransferListProps = {
  snapshot: ElecAdminAuditSnapshot
  year: number
}

const ChargePointsApplicationsList = ({
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
  const chargePointsApplicationsResponse = useQuery(
    apiAudit.getChargePointsApplications,
    {
      key: "audit-charge-points-applications",
      params: [query],
    }
  )

  const showChargePointsApplicationDetails = (
    chargePointApplication: ElecChargePointsApplication
  ) => {
    return {
      pathname: location.pathname,
      search: location.search,
      hash: `application/${chargePointApplication.id}`,
    }
  }

  const downloadChargePointsApplication = (
    chargePointApplication: ElecChargePointsApplication
  ) => {
    api.downloadChargePointsApplicationDetails(
      entity.id,
      chargePointApplication.cpo.id,
      chargePointApplication.id
    )
  }

  const chargePointsApplicationsData =
    chargePointsApplicationsResponse.result?.data.data

  const total = chargePointsApplicationsData?.total ?? 0
  const count = chargePointsApplicationsData?.returned ?? 0

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
            apiAudit.getElecAdminAuditChargePointsApplicationsFilters(
              filter,
              query
            )
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

        {count > 0 && chargePointsApplicationsData ? (
          <>
            <ChargePointsApplicationsTable
              loading={chargePointsApplicationsResponse.loading}
              applications={
                chargePointsApplicationsData.charge_points_applications
              }
              onDownloadChargePointsApplication={
                downloadChargePointsApplication
              }
              rowLink={showChargePointsApplicationDetails}
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
          <NoResult loading={chargePointsApplicationsResponse.loading} />
        )}
      </section>

      <HashRoute
        path="application/:id"
        element={<ChargePointsApplicationDetailsDialog />}
      />
    </>
  )
}
export default ChargePointsApplicationsList

// const FILTERS = [ElecAdminAuditFilter.Cpo]

export function useAutoStatus() {
  const matchStatus = useMatch(
    "/org/:entity/elec-admin-audit/:year/:view/:status/*"
  )
  const status =
    matchStatus?.params?.status?.toUpperCase() as ElecAdminAuditStatus
  return status ?? ElecAdminAuditStatus.Pending
}
