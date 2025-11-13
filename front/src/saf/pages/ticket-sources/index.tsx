import { useLocation } from "react-router-dom"

import useEntity from "common/hooks/entity"

import HashRoute from "common/components/hash-route"
import { SearchInput } from "common/components/inputs2"
import { ActionBar, Content } from "common/components/scaffold"
import { useQuery } from "common/hooks/async"
import {
  SafFilter,
  SafSnapshot,
  SafTicketSourcePreview,
  SafTicketSourceQueryBuilder,
} from "saf/types"
import * as api from "../../api"
import { SafFilters } from "saf/components/filters"
import { useAutoStatus } from "./index.hooks"
import { TicketDetails } from "saf/pages/ticket-details"
import TicketSourceDetail from "saf/pages/ticket-source-details"
import { StatusSwitcher } from "./components/status-switcher"
import TicketSourcesTable from "./components/table"
import { NoResult } from "common/components/no-result2"

import { useTranslation } from "react-i18next"
import { usePrivateNavigation } from "common/layouts/navigation"
import { ExportButton } from "common/components/export"
import { Pagination } from "common/components/pagination2"
import { RecapQuantity } from "common/molecules/recap-quantity"
import { formatUnit } from "common/utils/formatters"
import { Unit } from "common/types"
import { useQueryBuilder } from "common/hooks/query-builder-2"

export interface TicketSourcesProps {
  year: number
  snapshot: SafSnapshot | undefined
}

export const SafTicketSources = ({ year, snapshot }: TicketSourcesProps) => {
  const { t } = useTranslation()
  usePrivateNavigation(t("Volumes SAF"))

  const location = useLocation()

  const entity = useEntity()
  const status = useAutoStatus()

  const { query, state, actions } = useQueryBuilder<
    SafTicketSourceQueryBuilder["config"]
  >({
    status,
    year,
  })

  const ticketSourcesResponse = useQuery(api.getOperatorTicketSources, {
    key: "ticket-sources",
    params: [query],
  })

  const isAdmin = entity.isAdmin || entity.isExternal

  const ticketSourcesData = ticketSourcesResponse.result?.data
  const ids = ticketSourcesData?.results.map((ticket) => ticket.id)

  const total = ticketSourcesData?.count ?? 0
  const ticketSources = ticketSourcesData?.results

  const showTicketSourceDetail = (ticketSource: SafTicketSourcePreview) => {
    return {
      pathname: location.pathname,
      search: location.search,
      hash: `ticket-source/${ticketSource.id}`,
    }
  }

  const fetchIdsForPage = async (page: number) => {
    const response = await api.getOperatorTicketSources({
      ...query,
      page,
    })

    return response.data?.results ?? []
  }

  return (
    <>
      <StatusSwitcher
        onSwitch={actions.setStatus}
        count={snapshot}
        status={status}
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
          <ExportButton
            query={query}
            download={api.downloadOperatorTicketSources}
          />
        </ActionBar>
        <SafFilters
          filters={isAdmin ? ADMIN_FILTERS : FILTERS}
          selected={state.filters}
          onSelect={actions.setFilters}
          getFilterOptions={(filter) =>
            api.getTicketSourceFilters(filter, query)
          }
        />
        <RecapQuantity
          text={t("{{count}} volumes pour un total de {{total}}", {
            count: total,
            total: formatUnit(
              ticketSourcesData?.total_available_volume ?? 0,
              Unit.l
            ),
          })}
        />
        {ticketSources?.length && ticketSources ? (
          <>
            <TicketSourcesTable
              loading={ticketSourcesResponse.loading}
              order={state.order}
              ticketSources={ticketSources}
              rowLink={showTicketSourceDetail}
              selected={state.selection}
              onSelect={actions.setSelection}
              onOrder={actions.setOrder}
              status={status}
            />

            <Pagination
              defaultPage={state.page}
              limit={state.limit}
              total={total}
              onLimit={actions.setLimit}
            />
          </>
        ) : (
          <NoResult
            loading={ticketSourcesResponse.loading}
            filters={state.filters}
            onFilter={actions.setFilters}
          />
        )}
      </Content>

      <HashRoute
        path="ticket-source/:id"
        element={
          <TicketSourceDetail
            limit={state.limit}
            total={ticketSourcesData?.count ?? 0}
            fetchIdsForPage={fetchIdsForPage}
            baseIdsList={ids}
          />
        }
      />
      <HashRoute path="ticket/:id" element={<TicketDetails />} />
    </>
  )
}

const FILTERS = [
  SafFilter.Clients,
  SafFilter.Periods,
  SafFilter.Feedstocks,
  SafFilter.CountriesOfOrigin,
  SafFilter.ProductionSites,
  SafFilter.DeliverySites,
]

const ADMIN_FILTERS = [
  SafFilter.AddedBy, //
  SafFilter.Suppliers,
  ...FILTERS,
]
