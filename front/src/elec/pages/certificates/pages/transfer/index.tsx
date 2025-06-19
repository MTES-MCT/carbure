import { useLocation } from "react-router-dom"

import { SearchInput } from "common/components/inputs2"
import { ActionBar, Content } from "common/components/scaffold"
import { useTranslation } from "react-i18next"
import { usePrivateNavigation } from "common/layouts/navigation"
import { Tabs } from "common/components/tabs2"
import { Table } from "common/components/table2"
import { FilterMultiSelect2 } from "common/molecules/filter-multiselect2"
import { NoResult } from "common/components/no-result2"
import { Pagination } from "common/components/pagination2"
import { RecapQuantity } from "common/molecules/recap-quantity"
import { formatUnit } from "common/utils/formatters"
import { ExtendedUnit } from "common/types"
import { useQuery } from "common/hooks/async"
import { ElecCertificateSnapshot, TransferCertificate } from "../../types"
import {
  getTransferCertificates,
  getTransferCertificateFilters,
  exportTransferCertificates,
} from "../../api"
import {
  useColumns,
  useController,
  useFilters,
  useStatus,
  useTabs,
} from "./hooks"
import { normalizeSource } from "../../utils"
import { ExportButton } from "common/components/export"
import { normalizeBoolean, normalizeMonth } from "common/utils/normalizers"

export interface TransferCertificatesProps {
  year: number
  snapshot?: ElecCertificateSnapshot
}

export const TransferCertificates = ({
  year,
  snapshot,
}: TransferCertificatesProps) => {
  const { t } = useTranslation()

  usePrivateNavigation(t("Certificats de cession"))

  const location = useLocation()
  const status = useStatus()

  const { state, actions, query } = useController(year, status)

  const tabs = useTabs(snapshot)
  const filters = useFilters()
  const columns = useColumns()

  const transferCerts = useQuery(getTransferCertificates, {
    key: "elec-transfer-certificates",
    params: [query],
  })

  const loading = transferCerts.loading
  const data = transferCerts.result?.data
  const isEmpty = !data?.results.length

  const showTransferCertificateDetail = (p: TransferCertificate) => {
    return {
      pathname: location.pathname,
      search: location.search,
      hash: `transfer-certificate/${p.id}`,
    }
  }

  const getTransferCertificateFilter = (filter: string) =>
    getTransferCertificateFilters(filter, query)

  return (
    <>
      <Tabs //
        focus={status}
        tabs={tabs}
        keepSearch
      />

      <Content>
        <ActionBar>
          <ActionBar.Grow>
            <SearchInput
              debounce={250}
              value={state.search}
              onChange={actions.setSearch}
            />
          </ActionBar.Grow>

          <ExportButton query={query} download={exportTransferCertificates} />
        </ActionBar>

        <FilterMultiSelect2
          filterLabels={filters}
          selected={state.filters}
          onSelect={actions.setFilters}
          getFilterOptions={getTransferCertificateFilter}
          normalizers={{
            source: normalizeSource,
            month: normalizeMonth,
            used_in_tiruert: normalizeBoolean,
          }}
        />

        {isEmpty && (
          <NoResult
            loading={loading}
            filters={state.filters}
            onFilter={actions.setFilters}
          />
        )}

        {!isEmpty && (
          <>
            <RecapQuantity
              text={t(
                "{{count}} certificats, pour un total de {{total}} transférés",
                {
                  count: data.count,
                  total: formatUnit(
                    data!.transferred_energy ?? 0,
                    ExtendedUnit.MWh
                  ),
                }
              )}
            />

            <Table
              loading={loading}
              rowLink={showTransferCertificateDetail}
              order={state.order}
              onOrder={actions.setOrder}
              rows={data!.results}
              columns={columns}
            />

            <Pagination
              defaultPage={state.page}
              limit={state.limit}
              total={data!.count}
              onLimit={actions.setLimit}
            />
          </>
        )}
      </Content>
    </>
  )
}

export default TransferCertificates
