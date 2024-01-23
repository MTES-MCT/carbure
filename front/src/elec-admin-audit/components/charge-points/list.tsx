import useEntity from "carbure/hooks/entity"
import Button from "common/components/button"
import HashRoute from "common/components/hash-route"
import { Download } from "common/components/icons"
import NoResult from "common/components/no-result"
import Pagination from "common/components/pagination"
import { usePortal } from "common/components/portal"
import { ActionBar, Bar } from "common/components/scaffold"
import { useQuery } from "common/hooks/async"
import { useAdminTransferCertificateQueryParamsStore } from "elec-admin/hooks/transfer-certificate-query-params-store"
import { useAdminTransferCertificatesQuery } from "elec-admin/hooks/transfer-certificates-query"
import { ElecAdminSnapshot, ElecAdminTransferCertificateFilter } from "elec-admin/types"
import { ElecChargePointsApplication, ElecTransferCertificatePreview } from "elec/types"
import { ElecTransferCertificateStatus } from "elec/types-cpo"
import { useTranslation } from "react-i18next"
import { useLocation, useMatch } from "react-router-dom"
import * as api from "../../../elec-admin-audit/api"
import ElecAdminTransferDetailsDialog from "../../../elec-admin/components/transfer-certificate/details"
import TransferCertificateFilters from "../../../elec-admin/components/transfer-certificate/filters"
import ElecAdminTransferCertificateTable from "../../../elec-admin/components/transfer-certificate/table"
import { ElecAdminAuditFilter, ElecAdminAuditSnapshot, ElecAdminAuditStatus } from "elec-admin-audit/types"
import { useElecAdminAuditChargePointsQueryParamsStore } from "./list-query-params-store"
import { useElectAdminAuditQuery } from "./list-query"
import ElecAdminAuditFilters from "./list-filters"
import { elecAdminChargePointsApplicationsList } from "elec-admin-audit/__test__/data"
import { StatusSwitcher } from "./status-switcher"
import ChargePointsApplicationsTable from "elec/components/charge-points/table"
import ChargingPointsApplicationDetailsDialog from "./details"

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

  const chargePointsApplicationsData = elecAdminChargePointsApplicationsList
  // const chargePointsApplicationsData = chargePointsApplicationsResponse.result?.data.data

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
            api.getElecAdminAuditFilters(filter, query)
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
              onDownloadChargePointsApplication={() => { }}
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
  ElecAdminAuditFilter.Period
]


export function useAutoStatus() {
  const matchStatus = useMatch("/org/:entity/elec-admin-audit/:year/:view/:status/*")
  const status = matchStatus?.params?.status?.toUpperCase() as ElecAdminAuditStatus
  return status ?? ElecAdminAuditStatus.Pending
}
