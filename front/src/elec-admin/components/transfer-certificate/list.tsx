import useEntity from "carbure/hooks/entity"
import Button from "common/components/button"
import HashRoute from "common/components/hash-route"
import { Download } from "common/components/icons"
import NoResult from "common/components/no-result"
import Pagination from "common/components/pagination"
import { ActionBar, Bar } from "common/components/scaffold"
import { useQuery } from "common/hooks/async"
import { useCBQueryBuilder, useCBQueryParamsStore } from "common/hooks/query-builder"
import FilterMultiSelect from "common/molecules/filter-select"
import {
  ElecAdminSnapshot,
  ElecAdminTransferCertificateFilter
} from "elec-admin/types"
import { ElecTransferCertificatePreview } from "elec/types"
import { ElecTransferCertificateStatus } from "elec/types-cpo"
import { useTranslation } from "react-i18next"
import { useLocation, useMatch } from "react-router-dom"
import * as api from "../../api"
import ElecAdminTransferDetailsDialog from "./details"
import { usePageTitle } from "./page-title"
import { StatusSwitcher } from "./status-switcher"
import ElecAdminTransferCertificateTable from "./table"

type TransferListProps = {
  snapshot: ElecAdminSnapshot
  year: number
}

const TransferList = ({ snapshot, year }: TransferListProps) => {
  const entity = useEntity()
  const status = useAutoStatus()
  const { t } = useTranslation()
  const location = useLocation()

  const [state, actions] = useCBQueryParamsStore(
    entity,
    year,
    status,
    snapshot,
  )
  const query = useCBQueryBuilder(state);
  usePageTitle(state)
  const transferCertificatesResponse = useQuery(api.getTransferCertificates, {
    key: "transfer-certificates",
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
    [ElecAdminTransferCertificateFilter.Cpo]: t("Aménageur"),
    [ElecAdminTransferCertificateFilter.Operator]: t("Redevable"),
    [ElecAdminTransferCertificateFilter.TransferDate]: t("Date d'émission"),
    [ElecAdminTransferCertificateFilter.CertificateId]: t("Numéro"),
  }

  return (
    <>
      <Bar>
        <FilterMultiSelect
          filterLabels={filterLabels}
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

          {count > 0 && (
            <Button
              asideX={true}
              icon={Download}
              label={t("Exporter vers Excel")}
              action={() => api.downloadTransferCertificates(query)}
            />
          )}
        </ActionBar>

        {count > 0 && transferCertificatesData ? (
          <>
            <ElecAdminTransferCertificateTable
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
        element={<ElecAdminTransferDetailsDialog />}
      />
    </>
  )
}
export default TransferList

const FILTERS = [
  ElecAdminTransferCertificateFilter.Cpo,
  ElecAdminTransferCertificateFilter.Operator,
  ElecAdminTransferCertificateFilter.TransferDate,
  ElecAdminTransferCertificateFilter.CertificateId,
]

export function useAutoStatus() {
  const matchStatus = useMatch("/org/:entity/elec-admin/:year/:view/:status/*")
  const status =
    matchStatus?.params?.status?.toUpperCase() as ElecTransferCertificateStatus
  return status ?? ElecTransferCertificateStatus.Pending
}
