import useEntity from "carbure/hooks/entity"
import NoResult from "common/components/no-result"
import Pagination from "common/components/pagination"
import { ActionBar, Bar } from "common/components/scaffold"
import { useQuery } from "common/hooks/async"
import { useProvistionCertificateQueryParamsStore } from "elec-admin/hooks/provision-certificate-query-params-store"
import { useProvisionCertificatesQuery } from "elec-admin/hooks/provision-certificates-query"
import { ElecAdminProvisionCertificateFilter, ElecAdminProvisionCertificateStatus, ElecAdminSnapshot } from "elec-admin/types"
import { useMatch } from "react-router-dom"
import * as api from "../../api"
import ProvisionImporButton from "./Import-button"
import ProvisionCertificateFilters from "./filters"
import { StatusSwitcher } from "./status-switcher"
import ElecAdminProvisionCertificateTable from "./table"
import { elecAdminProvisionCertificateList } from "elec/__test__/data"

type ProvisionListProps = {
  snapshot: ElecAdminSnapshot
  year: number
}

const ProvisionList = ({ snapshot, year }: ProvisionListProps) => {

  const entity = useEntity()
  const status = useAutoStatus()
  const [state, actions] = useProvistionCertificateQueryParamsStore(entity, year, status, snapshot)
  const query = useProvisionCertificatesQuery(state)

  const provisionCertificatesResponse = useQuery(api.getProvisionCertificates, {
    key: "provision-certificates",
    params: [query],
  })

  // const showProvisionCertificateDetails = (provisionCertificate: ElecProvisionCertificatePreview) => {
  //   return {
  //     pathname: location.pathname,
  //     search: location.search,
  //     hash: `provision-certificate/${provisionCertificate.id}`,
  //   }
  // }

  // const provisionCertificatesData = provisionCertificatesResponse.result?.data.data
  const provisionCertificatesData = elecAdminProvisionCertificateList //TOTEST  

  const total = provisionCertificatesData?.total ?? 0
  const count = provisionCertificatesData?.returned ?? 0
  return (
    <>

      <Bar>
        <ProvisionCertificateFilters
          filters={FILTERS}
          selected={state.filters}
          onSelect={actions.setFilters}
          getFilterOptions={(filter) =>
            api.getProvisionCertificateFilters(filter, query)
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

          <ProvisionImporButton />
        </ActionBar>

        {count > 0 && provisionCertificatesData ? (
          <>
            <ElecAdminProvisionCertificateTable
              loading={provisionCertificatesResponse.loading}
              order={state.order}
              provisionCertificates={provisionCertificatesData.elec_provision_certificates}
              // rowLink={showProvisionCertificateDetails}
              selected={state.selection}
              onSelect={actions.setSelection}
              onOrder={actions.setOrder}
              status={status}
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
            loading={provisionCertificatesResponse.loading}
          // filters={state.filters}
          // onFilter={actions.setFilters}
          />
        )}
      </section >



    </>
  )
}
export default ProvisionList


const FILTERS = [
  ElecAdminProvisionCertificateFilter.Cpo,
  ElecAdminProvisionCertificateFilter.Quarter,
  ElecAdminProvisionCertificateFilter.OperatingUnit,
]


export function useAutoStatus() {
  const matchStatus = useMatch("/org/:entity/elec-admin/:year/:status/*")
  const status = matchStatus?.params?.status?.toUpperCase() as ElecAdminProvisionCertificateStatus
  return status ?? ElecAdminProvisionCertificateStatus.Available
}