import useEntity from "carbure/hooks/entity"
import HashRoute from "common/components/hash-route"
import NoResult from "common/components/no-result"
import Pagination from "common/components/pagination"
import { ActionBar, Bar } from "common/components/scaffold"
import { useQuery } from "common/hooks/async"
import { ElecAdminAuditFilter, ElecAdminAuditSnapshot, ElecAdminAuditStatus } from "elec-admin-audit/types"
import ChargePointsApplicationsTable from "elec/components/charge-points/table"
import { ElecChargePointsApplication } from "elec/types"
import { useTranslation } from "react-i18next"
import { useLocation, useMatch } from "react-router-dom"
import * as api from "../../../elec-admin-audit/api"
import ChargingPointsApplicationDetailsDialog from "./details"
import ElecAdminAuditFilters from "./list-filters"
import { useElectAdminAuditQuery } from "./list-query"
import { useElecAdminAuditChargePointsQueryParamsStore } from "./list-query-params-store"
import { StatusSwitcher } from "./status-switcher"

type TransferListProps = {
  snapshot: ElecAdminAuditSnapshot
  year: number
}

const ChargePointsApplicationsList = ({ snapshot, year }: TransferListProps) => {

  const entity = useEntity()
  const status = useAutoStatus()
  const { t } = useTranslation()
  const location = useLocation()

  const [state, actions] = useElecAdminAuditChargePointsQueryParamsStore(entity, year, status, snapshot)
  const query = useElectAdminAuditQuery(state)
  const chargePointsApplicationsResponse = useQuery(api.getChargePointsApplications, {
    key: "audit-charge-points-applications",
    params: [query],
  })

  const showChargePointsApplicationDetails = (chargePointApplication: ElecChargePointsApplication) => {
    return {
      pathname: location.pathname,
      search: location.search,
      hash: `application/${chargePointApplication.id}`,
    }

  }

  const downloadChargePointsApplication = (chargePointApplication: ElecChargePointsApplication) => {
    api.downloadChargePointsApplication(entity.id, chargePointApplication.id)
  }

  // const chargePointsApplicationsData = elecAdminChargePointsApplicationsList
  const chargePointsApplicationsData = chargePointsApplicationsResponse.result?.data.data

  const total = chargePointsApplicationsData?.total ?? 0
  const count = chargePointsApplicationsData?.returned ?? 0
  return (
    <>

      <Bar>
        <ElecAdminAuditFilters
          filters={FILTERS}
          selected={state.filters}
          onSelect={actions.setFilters}
          getFilterOptions={(filter) =>
            api.getElecAdminAuditChargePointsApplicationsFilters(filter, query)
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
              applications={chargePointsApplicationsData.charge_points_applications}
              onDownloadChargePointsApplication={downloadChargePointsApplication}
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
  ElecAdminAuditFilter.Cpo,
  // ElecAdminAuditFilter.Period
]


export function useAutoStatus() {
  const matchStatus = useMatch("/org/:entity/elec-admin-audit/:year/:view/:status/*")
  const status = matchStatus?.params?.status?.toUpperCase() as ElecAdminAuditStatus
  return status ?? ElecAdminAuditStatus.Pending
}
