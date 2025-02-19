import { useLocation } from "react-router-dom"

import useEntity from "common/hooks/entity"

import HashRoute from "common/components/hash-route"
import { SearchInput } from "common/components/inputs2"
import { ActionBar, Content } from "common/components/scaffold"
import { useQuery } from "common/hooks/async"
import {
  SafFilter,
  SafOperatorColumnsOrder,
  SafOperatorSnapshot,
} from "saf/types"
import LotDetails from "transaction-details/components/lots"
import * as api from "../api"
import { SafFilters } from "../../../components/filters"
import { useAutoStatus } from "./index.hooks"
import { OperatorTicketDetails } from "../ticket-details"
import TicketSourceDetail from "../ticket-source-details"
import { StatusSwitcher } from "./status-switcher"
import TicketSourcesTable from "./table"
import { NoResult } from "common/components/no-result2"
import {
  useCBQueryBuilder,
  useCBQueryParamsStore,
} from "common/hooks/query-builder-2"
import { SafTicketSource, SafTicketSourceStatus } from "../types"
import { useTranslation } from "react-i18next"
import { usePrivateNavigation } from "common/layouts/navigation"
import { ExportButton } from "saf/components/export"
import { Pagination } from "common/components/pagination2"

export interface TicketSourcesProps {
  year: number
  snapshot: SafOperatorSnapshot | undefined
}

export const TicketSources = ({ year, snapshot }: TicketSourcesProps) => {
  const { t } = useTranslation()
  usePrivateNavigation(t("Volumes SAF"))

  const location = useLocation()

  const entity = useEntity()
  const status = useAutoStatus()

  const [state, actions] = useCBQueryParamsStore<
    SafTicketSourceStatus,
    undefined
  >(entity, year, status)

  const query = useCBQueryBuilder<
    SafOperatorColumnsOrder[],
    SafTicketSourceStatus,
    undefined
  >(state)

  const ticketSourcesResponse = useQuery(api.getOperatorTicketSources, {
    key: "ticket-sources",
    params: [query],
  })

  const ticketSoucesData = ticketSourcesResponse.result?.data
  const ids = ticketSoucesData?.results.map((ticket) => ticket.id)

  const total = ticketSoucesData?.count ?? 0
  const count = ticketSoucesData?.results.length ?? 0
  const ticketSources = ticketSoucesData?.results

  const showTicketSourceDetail = (ticketSource: SafTicketSource) => {
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
              clear
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
          filters={FILTERS}
          selected={state.filters}
          onSelect={actions.setFilters}
          getFilterOptions={(filter) =>
            api.getTicketSourceFilters(filter, query)
          }
        />

        {count > 0 && ticketSources ? (
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

            {(state.limit ?? 0) < total && (
              <Pagination
                defaultPage={state.page}
                limit={state.limit}
                total={total}
              />
            )}
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
            total={ticketSoucesData?.count ?? 0}
            fetchIdsForPage={fetchIdsForPage}
            baseIdsList={ids}
          />
        }
      />
      <HashRoute path="lot/:id" element={<LotDetails />} />
      <HashRoute path="ticket/:id" element={<OperatorTicketDetails />} />
    </>
  )
}

const FILTERS = [
  SafFilter.Suppliers,
  SafFilter.Clients,
  SafFilter.Periods,
  SafFilter.Feedstocks,
  SafFilter.CountriesOfOrigin,
  SafFilter.ProductionSites,
  SafFilter.DeliverySites,
]

export default TicketSources
