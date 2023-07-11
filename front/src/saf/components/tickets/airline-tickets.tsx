import { useLocation } from "react-router-dom"

import useEntity from "carbure/hooks/entity"

import HashRoute from "common/components/hash-route"
import { SearchInput } from "common/components/input"
import { ActionBar, Bar } from "common/components/scaffold"
import { useQuery } from "common/hooks/async"
import { useQueryParamsStore } from "saf/hooks/query-params-store"
import { useSafQuery } from "saf/hooks/saf-query"
import {
  SafClientSnapshot,
  SafFilter,
  SafQuery,
  SafTicket,
  SafTicketStatus,
} from "saf/types"
import * as api from "../../api"
import { Filters } from "../filters"
import { useAutoStatus } from "../client-tabs"
import { ClientTicketDetails } from "../ticket-details/airline-details"
import TicketsTable from "./table"

export interface AirlineTicketsProps {
  year: number
  snapshot?: SafClientSnapshot
}

export const AirlineTickets = ({ year, snapshot }: AirlineTicketsProps) => {
  const location = useLocation()

  const entity = useEntity()
  const status = useAutoStatus()
  const [state, actions] = useQueryParamsStore(entity, year, status, snapshot)
  const query = useSafQuery(state)

  const apiGetTickets = (query: SafQuery) => api.getSafAirlineTickets(query)

  const ticketsResponse = useQuery(apiGetTickets, {
    key: "tickets",
    params: [query],
  })

  const ticketsData = ticketsResponse.result?.data.data
  const ids = ticketsData?.ids ?? []

  const showTicketDetail = (ticket: SafTicket) => {
    return {
      pathname: location.pathname,
      search: location.search,
      hash: `ticket/${ticket.id}`,
    }
  }

  const getTicketFilter = (filter: any) => {
    return api.getAirlineTicketFilters(filter, query)
  }

  return (
    <>
      <Bar>
        <Filters
          filters={CLIENT_FILTERS}
          selected={state.filters}
          onSelect={actions.setFilters}
          getFilterOptions={getTicketFilter}
        />
      </Bar>
      <section>
        <ActionBar>
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
