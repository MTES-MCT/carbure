import useEntity from "carbure/hooks/entity"
import NoResult from "common/components/no-result"
import Pagination from "common/components/pagination"
import { Bar } from "common/components/scaffold"
import { useQuery } from "common/hooks/async"
import { useProvistionCertificateQueryParamsStore } from "elec-admin/hooks/provision-certificate-query-params-store"
import { useProvisionCertificatesQuery } from "elec-admin/hooks/provision-certificates-query"
import { ElecAdminProvisionCertificateStatus, ElecAdminSnapshot, ElecAdminTransferCertificateFilter } from "elec-admin/types"
import { useMatch } from "react-router-dom"
import * as api from "../../api"
import TransferCertificateFilters from "./filters"
import ElecAdminTransferCertificateTable from "./table"

type TransferListProps = {
  snapshot: ElecAdminSnapshot
  year: number
}

const TransferList = ({ snapshot, year }: TransferListProps) => {

  const entity = useEntity()
  const status = useAutoStatus()
  const [state, actions] = useProvistionCertificateQueryParamsStore(entity, year, status, snapshot)
  const query = useProvisionCertificatesQuery(state)

  const transferCertificatesResponse = useQuery(api.getTransferCertificates, {
    key: "transfer-certificates",
    params: [query],
  })

  // const showProvisionCertificateDetails = (provisionCertificate: ElecProvisionCertificatePreview) => {
  //   return {
  //     pathname: location.pathname,
  //     search: location.search,
  //     hash: `provision-certificate/${provisionCertificate.id}`,
  //   }
  // }

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


        {/* <ActionBar>

          <StatusSwitcher
            status={status}
            onSwitch={actions.setStatus}
            snapshot={snapshot}
          />

          <ProvisionImporButton />
        </ActionBar> */}

        {count > 0 && transferCertificatesData ? (
          <>
            <ElecAdminTransferCertificateTable
              loading={transferCertificatesResponse.loading}
              order={state.order}
              transferCertificates={transferCertificatesData.elec_transfer_certificates}
              // rowLink={showProvisionCertificateDetails}
              selected={state.selection}
              onSelect={actions.setSelection}
              onOrder={actions.setOrder}
            // status={status}
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
  const matchStatus = useMatch("/org/:entity/elec-admin/:year/:status/*")
  const status = matchStatus?.params?.status?.toUpperCase() as ElecAdminProvisionCertificateStatus
  return status ?? ElecAdminProvisionCertificateStatus.Available
}