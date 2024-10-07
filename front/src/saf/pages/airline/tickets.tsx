import { useLocation } from "react-router-dom"

import useEntity from "carbure/hooks/entity"

import HashRoute from "common/components/hash-route"
import { SearchInput } from "common/components/input"
import { ActionBar, Bar } from "common/components/scaffold"
import { useQuery } from "common/hooks/async"
import {
  SafClientSnapshot,
  SafColumsOrder,
  SafFilter,
  SafQuery,
  SafStates,
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
  snapshot?: SafClientSnapshot
}

export const AirlineTickets = ({ year, snapshot }: AirlineTicketsProps) => {
  const location = useLocation()

  const entity = useEntity()
  const status = useAutoStatus()
  const [state, actions] = useCBQueryParamsStore<SafStates>(
    entity,
    year,
    status,
    snapshot
  )

  const query = useCBQueryBuilder<SafColumsOrder[]>(state)
  const apiGetTickets = (query: SafQuery) => api.getSafAirlineTickets(query)

  const ticketsResponse = useQuery(apiGetTickets, {
    key: "tickets",
    params: [query],
  })

  // const ticketsData = ticketsResponse.result?.data.data
  const ticketsData = ticketsResponse.result?.data?.results
  // const ids = ticketsData?.ids ?? []
  const ids: any = []

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
          status={status as SafTicketStatus}
          ticketsData={ticketsData}
          rowLink={showTicketDetail}
        />
      </section>

      <HashRoute
        path="ticket/:id"
        element={<ClientTicketDetails neighbors={ids} />}
      />
    </>
  )
}

const CLIENT_FILTERS = [
  SafFilter.Suppliers,
  SafFilter.Periods,
  SafFilter.Feedstocks,
]

export default AirlineTickets
