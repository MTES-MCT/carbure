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
import FilterMultiSelect from "common/molecules/filter-select"
import {
  ElecTransferCertificateFilter,
  ElecTransferCertificatePreview,
} from "elec/types"
import { ElecCPOSnapshot, ElecTransferCertificateStatus } from "elec/types-cpo"
import { useTranslation } from "react-i18next"
import { useLocation, useMatch } from "react-router-dom"
import * as api from "../../api-cpo"
import { StatusSwitcher } from "./cpo-status-switcher"
import ElecTransferDetailsDialog from "./details"
import ElecTransferCertificateTable from "./table"
import { usePrivateNavigation } from "common/layouts/navigation"

type CPOTransferCertificateListProps = {
  snapshot: ElecCPOSnapshot
  year: number
}

const CPOTransferCertificateList = ({
  snapshot,
  year,
}: CPOTransferCertificateListProps) => {
  const entity = useEntity()
  const status = useAutoStatus()
  const [state, actions] = useCBQueryParamsStore(entity, year, status, snapshot)
  const { t } = useTranslation()
  usePrivateNavigation(t("Énergie cédée"))

  const query = useCBQueryBuilder(state)
  const location = useLocation()

  const transferCertificatesResponse = useQuery(api.getTransferCertificates, {
    key: "elec-transfer-certificates",
    params: [query],
  })

  const showTransferCertificateDetails = (
    transferCertificate: ElecTransferCertificatePreview
  ) => {
    return {
      pathname: location.pathname,
      search: location.search,
      hash: `transfer-certificate/${transferCertificate.id}`,
    }
  }

  const transferCertificatesData =
    transferCertificatesResponse.result?.data.data

  const total = transferCertificatesData?.total ?? 0
  const count = transferCertificatesData?.returned ?? 0

  const filterLabels = {
    [ElecTransferCertificateFilter.Operator]: t("Redevable"),
    [ElecTransferCertificateFilter.Cpo]: t("Aménageur"),
    [ElecTransferCertificateFilter.TransferDate]: t("Date d'émission"),
    [ElecTransferCertificateFilter.CertificateId]: t("Numéro"),
  }
  return (
    <>
      <Bar>
        <FilterMultiSelect
          filterLabels={filterLabels}
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
            <ElecTransferCertificateTable
              loading={transferCertificatesResponse.loading}
              order={state.order}
              transferCertificates={
                transferCertificatesData.elec_transfer_certificates
              }
              rowLink={showTransferCertificateDetails}
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
          <NoResult loading={transferCertificatesResponse.loading} />
        )}
      </section>
      <HashRoute
        path="transfer-certificate/:id"
        element={<ElecTransferDetailsDialog />}
      />
    </>
  )
}
export default CPOTransferCertificateList

// const FILTERS = [
//   ElecTransferCertificateFilter.Operator,
//   ElecTransferCertificateFilter.TransferDate,
//   ElecTransferCertificateFilter.CertificateId,
// ]

export function useAutoStatus() {
  const matchStatus = useMatch("/org/:entity/elec/:year/:view/:status/*")
  const status =
    matchStatus?.params?.status?.toUpperCase() as ElecTransferCertificateStatus
  return status ?? ElecTransferCertificateStatus.Pending
}
