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
import {
  ElecCertificateSnapshot,
  ProvisionCertificate,
  ProvisionCertificateFilter,
  ProvisionCertificatesQueryBuilder,
} from "../../types"
import {
  getProvisionCertificates,
  getProvisionCertificateFilters,
  exportProvisionCertificates,
} from "../../api"
import { useColumns, useFilters, useStatus, useTabs } from "./hooks"
import { normalizeSource } from "../../utils"
import { ExportButton } from "common/components/export"
import { useQueryBuilder } from "common/hooks/query-builder-2"

export interface ProvisionCertificatesProps {
  year: number
  snapshot?: ElecCertificateSnapshot
}

export const ProvisionCertificates = ({
  year,
  snapshot,
}: ProvisionCertificatesProps) => {
  const { t } = useTranslation()

  usePrivateNavigation(t("Certificats de fourniture"))

  const location = useLocation()
  const status = useStatus()

  const { state, actions, query } = useQueryBuilder<
    ProvisionCertificatesQueryBuilder["config"]
  >({
    year,
    status,
  })

  const tabs = useTabs(snapshot)
  const filters = useFilters()
  const columns = useColumns()

  const provisionCerts = useQuery(getProvisionCertificates, {
    key: "elec-provision-certificates",
    params: [query],
  })

  const loading = provisionCerts.loading
  const data = provisionCerts.result?.data
  const isEmpty = !data?.results.length

  const showProvisionCertificateDetail = (p: ProvisionCertificate) => {
    return {
      pathname: location.pathname,
      search: location.search,
      hash: `provision-certificate/${p.id}`,
    }
  }

  const getProvisionCertificateFilter = (filter: ProvisionCertificateFilter) =>
    getProvisionCertificateFilters(filter, query)

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

          <ExportButton query={query} download={exportProvisionCertificates} />
        </ActionBar>

        <FilterMultiSelect2
          filterLabels={filters}
          selected={state.filters}
          onSelect={actions.setFilters}
          getFilterOptions={getProvisionCertificateFilter}
          normalizers={{ source: normalizeSource }}
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
                "{{count}} certificats et {{total}} d'énergie disponible pour cession",
                {
                  count: data.count,
                  total: formatUnit(
                    data!.available_energy ?? 0,
                    ExtendedUnit.MWh
                  ),
                }
              )}
            />

            <Table
              loading={loading}
              rowLink={showProvisionCertificateDetail}
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

export default ProvisionCertificates
