import useEntity from "carbure/hooks/entity"
import NoResult from "common/components/no-result"
import Pagination from "common/components/pagination"
import { usePortal } from "common/components/portal"
import { ActionBar, Bar } from "common/components/scaffold"
import { useQuery } from "common/hooks/async"
import { useAdminTransferCertificateQueryParamsStore } from "elec-admin/hooks/transfer-certificate-query-params-store"
import { useAdminTransferCertificatesQuery } from "elec-admin/hooks/transfer-certificates-query"
import { ElecAdminSnapshot, ElecAdminTransferCertificateFilter } from "elec-admin/types"
import { ElecCPOTransferCertificateStatus } from "elec/types-cpo"
import { useMatch } from "react-router-dom"
import * as api from "../../api"
import ElectTransferDetailsDialog from "../../../elec/components/transfer-certificates/details"
import TransferCertificateFilters from "./filters"
import { StatusSwitcher } from "./status-switcher"
import ElecAdminTransferCertificateTable from "./table"
import { ElecTransferCertificatePreview } from "elec/types"

type TransferListProps = {
  snapshot: ElecAdminSnapshot
  year: number
}

const TransferList = ({ snapshot, year }: TransferListProps) => {

  const entity = useEntity()
  const status = useAutoStatus()
  const portal = usePortal()

  const [state, actions] = useAdminTransferCertificateQueryParamsStore(entity, year, status, snapshot)
  const query = useAdminTransferCertificatesQuery(state)
  const transferCertificatesResponse = useQuery(api.getTransferCertificates, {
    key: "transfer-certificates",
    params: [query],
  })

  const showTransferCertificateDetails = (transferCertificate: ElecTransferCertificatePreview) => {
    portal((close) => <ElectTransferDetailsDialog
      onClose={close}
      transfer_certificate={transferCertificate} />)

  }

  const transferCertificatesData = transferCertificatesResponse.result?.data.data



  const total = transferCertificatesData?.total ?? 0
  const count = transferCertificatesData?.returned ?? 0
  return (
    <>

      <Bar>
        <TransferCertificateFilters
          filters={FILTERS}
          selected={state.filters}
          onSelect={actions.setFilters}
          getFilterOptions={(filter) =>
            api.getTransferCertificateFilters(filter, query)
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

        {count > 0 && transferCertificatesData ? (
          <>
            <ElecAdminTransferCertificateTable
              loading={transferCertificatesResponse.loading}
              order={state.order}
              transferCertificates={transferCertificatesData.elec_transfer_certificates}
              onAction={showTransferCertificateDetails}
              selected={state.selection}
              onSelect={actions.setSelection}
              onOrder={actions.setOrder}
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
            loading={transferCertificatesResponse.loading}
          // filters={state.filters}
          // onFilter={actions.setFilters}
          />
        )}
      </section >



    </>
  )
}
export default TransferList


const FILTERS = [
  ElecAdminTransferCertificateFilter.Cpo,
  ElecAdminTransferCertificateFilter.Operator,
  ElecAdminTransferCertificateFilter.TransferDate,
  ElecAdminTransferCertificateFilter.CertificateId
]


export function useAutoStatus() {
  const matchStatus = useMatch("/org/:entity/elec-admin/:year/:view/:status/*")
  const status = matchStatus?.params?.status?.toUpperCase() as ElecCPOTransferCertificateStatus
  return status ?? ElecCPOTransferCertificateStatus.Pending
}