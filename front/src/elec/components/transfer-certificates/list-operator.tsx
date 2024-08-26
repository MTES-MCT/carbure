import useEntity from "carbure/hooks/entity"
import Alert from "common/components/alert"
import Button from "common/components/button"
import HashRoute from "common/components/hash-route"
import { Bolt, Download } from "common/components/icons"
import NoResult from "common/components/no-result"
import Pagination from "common/components/pagination"
import { ActionBar, Bar } from "common/components/scaffold"
import { useQuery } from "common/hooks/async"
import { formatNumber } from "common/utils/formatters"
import {
  ElecTransferDetailsDialog,
} from "elec/components/transfer-certificates/details"

import {
  ElecTransferCertificateFilter,
  ElecTransferCertificatePreview,
} from "elec/types"
import { ElecOperatorSnapshot, ElecOperatorStatus } from "elec/types-operator"
import { useTranslation } from "react-i18next"
import { useLocation, useMatch } from "react-router-dom"
import * as api from "../../api-operator"
import ElecTransferCertificateTable from "./table"
import { useCBQueryBuilder, useCBQueryParamsStore } from "common/hooks/query-builder"
import FilterMultiSelect from "common/molecules/filter-select"

type OperatorTransferCertificateListProps = {
  snapshot: ElecOperatorSnapshot
  year: number
}

const OperatorTransferCertificateList = ({
  snapshot,
  year,
}: OperatorTransferCertificateListProps) => {
  const entity = useEntity()
  const status = useAutoStatus()
  const [state, actions] = useCBQueryParamsStore(
    entity,
    year,
    status,
    snapshot
  )
  const query = useCBQueryBuilder(state)
  const { t } = useTranslation()
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
        <Alert variant="info" icon={Bolt}>
          {t("{{acquired_energy}} MWh acquis", {
            count: snapshot.acquired_energy,
            acquired_energy: formatNumber(snapshot.acquired_energy, 3),
          })}
        </Alert>
      </Bar>

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
          {count > 0 && state.status === ElecOperatorStatus.Accepted && (
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
            <ElecTransferCertificateTable
              displayCpo={true}
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
        element={<ElecTransferDetailsDialog displayCpo={true} />}
      />
    </>
  )
}
export default OperatorTransferCertificateList

const FILTERS = [
  ElecTransferCertificateFilter.TransferDate,
  ElecTransferCertificateFilter.Cpo,
  ElecTransferCertificateFilter.CertificateId,
]

export function useAutoStatus() {
  const matchStatus = useMatch("/org/:entity/elec/:year/:status/*")
  const status =
    matchStatus?.params?.status?.toUpperCase() as ElecOperatorStatus
  return status ?? ElecOperatorStatus.Pending
}
