import { useLocation } from "react-router-dom"

import useEntity from "carbure/hooks/entity"

import HashRoute from "common/components/hash-route"
import { SearchInput } from "common/components/input"
import Pagination from "common/components/pagination"
import { ActionBar, Bar } from "common/components/scaffold"
import { useQuery } from "common/hooks/async"
import { useMemo } from "react"
import { useQueryParamsStore } from "saf/hooks/query-params-store"
import { useSafQuery } from "saf/hooks/saf-query"
import {
  SafClientSnapshot,
  SafFilter,
  SafOperatorSnapshot,
  SafQuery,
  SafStates,
  SafTicket,
  SafTicketStatus,
} from "saf/types"
import * as api from "../../api"
import * as data from "../../__test__/data"
import { Filters } from "../filters"
import NoResult from "../no-result"
import { useAutoStatus } from "../operator-tabs"
import { ClientTicketDetails } from "../ticket-details/airline-details"
import { OperatorTicketDetails } from "../ticket-details/operator-details"
import { StatusSwitcher } from "./status-switcher"
import TicketsTable from "./table"
import { EntityType } from "carbure/types"

export interface OperatorTicketsProps {
  year: number
  snapshot?: SafOperatorSnapshot
}

export const OperatorTickets = ({ year, snapshot }: OperatorTicketsProps) => {
  const location = useLocation()

  const entity = useEntity()
  const status = useAutoStatus()
  const [state, actions] = useQueryParamsStore(entity, year, status, snapshot)
  const query = useSafQuery(state)

  const apiGetTickets = (query: SafQuery) => api.getOperatorTickets(query)

  const ticketsResponse = useQuery(apiGetTickets, {
    key: "tickets",
    params: [query],
  })

  const ticketsData = ticketsResponse.result?.data.data
  // const ticketsData = data.safTicketsResponse //TO TEST with testing d:ata
  const ids = ticketsData?.ids ?? []

  const showTicketDetail = (ticket: SafTicket) => {
    return {
      pathname: location.pathname,
      search: location.search,
      hash: `ticket/${ticket.id}`,
    }
  }

  const getTicketFilter = (filter: any) =>
    api.getOperatorTicketFilters(filter, query)

  return (
    <>
      <Bar>
        <Filters
          filters={OPERATOR_FILTERS}
          selected={state.filters}
          onSelect={actions.setFilters}
          getFilterOptions={getTicketFilter}
        />
      </Bar>
      <section>
        <ActionBar>
          {entity.isOperator && (
            <StatusSwitcher
              onSwitch={actions.setStatus}
              count={snapshot as SafOperatorSnapshot}
              status={status as SafTicketStatus}
            />
          )}

          <SearchInput
            asideX
            clear
            debounce={250}
            value={state.search}
            onChange={actions.setSearch}
          />
        </ActionBar>

        <TicketsTable
          loading={false}
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
        element={<OperatorTicketDetails neighbors={ids} />}
      />
    </>
  )
}

const OPERATOR_FILTERS = [
  SafFilter.Clients,
  SafFilter.Periods,
  SafFilter.Feedstocks,
]

export default OperatorTickets
