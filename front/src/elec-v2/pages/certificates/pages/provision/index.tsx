import { useLocation, useParams } from "react-router-dom"

import useEntity from "common/hooks/entity"

import { SearchInput } from "common/components/inputs2"
import { ActionBar, Content } from "common/components/scaffold"
import { useQuery } from "common/hooks/async"
import {
  useCBQueryBuilder,
  useCBQueryParamsStore,
} from "common/hooks/query-builder-2"
import { useTranslation } from "react-i18next"
import { usePrivateNavigation } from "common/layouts/navigation"
import { getProvisionCertificateFilters, getProvisionCertificates } from "./api"
import {
  ProvisionCertificate,
  ProvisionCertificateFilter,
  ProvisionCertificateOrder,
  ProvisionCertificateStatus,
} from "./types"
import { Tabs } from "common/components/tabs2"
import { Table } from "common/components/table2"
import { useColumns, useFilters, useTabs } from "./hooks"
import { FilterMultiSelect2 } from "common/molecules/filter-multiselect2"
import { NoResult } from "common/components/no-result2"

export interface ProvisionCertificatesProps {
  year: number
}

export const ProvisionCertificates = ({ year }: ProvisionCertificatesProps) => {
  const { t } = useTranslation()

  usePrivateNavigation(t("Certificats de fourniture"))

  const entity = useEntity()

  const location = useLocation()
  const params = useParams<"status">()
  const status = (params.status ?? "available") as ProvisionCertificateStatus

  const tabs = useTabs()
  const filters = useFilters()
  const columns = useColumns()

  const [state, actions] = useCBQueryParamsStore<
    ProvisionCertificateStatus,
    undefined
  >(entity, year, status)

  const query = useCBQueryBuilder<
    ProvisionCertificateOrder[],
    ProvisionCertificateStatus,
    undefined
  >(state)

  const provisionResponse = useQuery(getProvisionCertificates, {
    key: "tickets",
    params: [query],
  })

  const provisionData = provisionResponse.result?.data
  const isEmpty = !provisionData?.results.length

  const showTicketDetail = (p: ProvisionCertificate) => {
    return {
      pathname: location.pathname,
      search: location.search,
      hash: `provision-certificate/${p.id}`,
    }
  }

  const getTicketFilter = (filter: ProvisionCertificateFilter) =>
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
        </ActionBar>

        <FilterMultiSelect2
          filterLabels={filters}
          selected={state.filters}
          onSelect={actions.setFilters}
          getFilterOptions={getTicketFilter}
        />

        {isEmpty && (
          <NoResult
            loading={provisionResponse.loading}
            filters={state.filters}
            onFilter={actions.setFilters}
          />
        )}

        {!isEmpty && (
          <Table
            loading={provisionResponse.loading}
            rowLink={showTicketDetail}
            order={state.order}
            onOrder={actions.setOrder}
            rows={provisionData?.results ?? []}
            columns={[
              columns.period,
              columns.operatingUnit,
              columns.source,
              columns.energy,
            ]}
          />
        )}
      </Content>
    </>
  )
}

export default ProvisionCertificates
