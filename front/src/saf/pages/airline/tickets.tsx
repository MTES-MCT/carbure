import { useLocation } from "react-router-dom"

import useEntity from "common/hooks/entity"

import HashRoute from "common/components/hash-route"
import { SearchInput } from "common/components/input"
import { ActionBar, Bar } from "common/components/scaffold"
import { useQuery } from "common/hooks/async"
import {
  SafColumsOrder,
  SafFilter,
  SafQuery,
  SafTicket,
  SafTicketStatus,
} from "saf/types"
import * as api from "./api"
import { SafFilters } from "../../components/filters"
import { useAutoStatus } from "./tabs"
import { ClientTicketDetails } from "./ticket-details"
import TicketsTable from "../../components/tickets/table"
import { ExportButton } from "../operator/ticket-source-details/export"
import {
  useCBQueryBuilder,
  useCBQueryParamsStore,
} from "common/hooks/query-builder-2"

export interface AirlineTicketsProps {
  year: number
}

export const AirlineTickets = ({ year }: AirlineTicketsProps) => {
  const location = useLocation()

  const entity = useEntity()
  const status = useAutoStatus()
  const [state, actions] = useCBQueryParamsStore<SafTicketStatus, undefined>(
    entity,
    year,
    status
  )

  const query = useCBQueryBuilder<SafColumsOrder[], SafTicketStatus, undefined>(
    state
  )
  const apiGetTickets = (query: SafQuery) => {
    return api.getSafAirlineTickets(query)
  }

  const ticketsResponse = useQuery(apiGetTickets, {
    key: "tickets",
    params: [query],
  })

  const fetchIdsForPage = async (page: number) => {
    const response = await apiGetTickets({
      ...query,
      page,
    })

    return response.data?.results ?? []
  }

  const ticketsData = ticketsResponse.result?.data

  const ids = ticketsData?.results.map((ticket) => ticket.id) || []

  const showTicketDetail = (ticket: SafTicket) => {
    return {
      pathname: location.pathname,
      search: location.search,
      hash: `ticket/${ticket.id}`,
    }
  }

  const getTicketFilter = (filter: SafFilter) => {
    return api.getAirlineTicketFilters(filter, query)
  }

  return (
    <>
      <Bar>
        <SafFilters
          filters={CLIENT_FILTERS}
          selected={state.filters}
          onSelect={actions.setFilters}
          getFilterOptions={getTicketFilter}
        />
      </Bar>
      <section>
        <ActionBar>
          <ExportButton
            query={query}
            download={api.downloadSafAirlineTickets}
          />
          <SearchInput
            asideX
            clear
            debounce={250}
            value={state.search}
            onChange={actions.setSearch}
          />
        </ActionBar>

        <TicketsTable
          client
          loading={ticketsResponse.loading}
          state={state}
          actions={actions}
          order={state.order}
          status={status}
          ticketsData={ticketsData}
          rowLink={showTicketDetail}
        />
      </section>

      {ticketsData && (
        <HashRoute
          path="ticket/:id"
          element={
            <ClientTicketDetails
              limit={state.limit}
              total={ticketsData?.count || 0}
              fetchIdsForPage={fetchIdsForPage}
              baseIdsList={ids}
            />
          }
        />
      )}
    </>
  )
}

const CLIENT_FILTERS = [
  SafFilter.Suppliers,
  SafFilter.Periods,
  SafFilter.Feedstocks,
]

export default AirlineTickets
