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

export interface TicketsProps {
  year: number
  snapshot?: SafOperatorSnapshot | SafClientSnapshot
}

export const Tickets = ({ year, snapshot }: TicketsProps) => {
  const location = useLocation()

  const entity = useEntity()
  const status = useAutoStatus()
  const [state, actions] = useQueryParamsStore(entity, year, status, snapshot)
  const query = useSafQuery(state)

  const apiGetTickets = (query: SafQuery) => {
    return entity.entity_type === EntityType.Operator
      ? api.getOperatorTickets(query)
      : api.getSafAirlineTickets(query)
  }

  const ticketsResponse = useQuery(apiGetTickets, {
    key: "tickets",
    params: [query],
  })

  const ticketsData = ticketsResponse.result?.data.data
  // const ticketsData = data.safTicketsResponse //TO TEST with testing d:ata
  const ids = ticketsData?.ids ?? []

  const total = ticketsData?.total ?? 0
  const count = ticketsData?.returned ?? 0
  const tickets = ticketsData?.saf_tickets

  const showTicketDetail = (ticket: SafTicket) => {
    return {
      pathname: location.pathname,
      search: location.search,
      hash: `ticket/${ticket.id}`,
    }
  }

  const getTicketFilter = (filter: any) => {
    return entity.entity_type === EntityType.Operator
      ? api.getOperatorTicketFilters(filter, query)
      : api.getAirlineTicketFilters(filter, query)
  }

  return (
    <>
      <Bar>
        <Filters
          filters={entity.isAirline ? CLIENT_FILTERS : OPERATOR_FILTERS}
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

        {count > 0 && tickets ? (
          <>
            <TicketsTable
              loading={false}
              order={state.order}
              status={status as SafTicketStatus}
              tickets={tickets}
              rowLink={showTicketDetail}
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
          <NoResult
            loading={ticketsResponse.loading}
            filters={state.filters}
            onFilter={actions.setFilters}
          />
        )}
      </section>

      <HashRoute
        path="ticket/:id"
        element={
          entity.isOperator ? (
            <OperatorTicketDetails neighbors={ids} />
          ) : (
            <ClientTicketDetails neighbors={ids} />
          )
        }
      />
    </>
  )
}

const OPERATOR_FILTERS = [
  SafFilter.Clients,
  SafFilter.Periods,
  SafFilter.Feedstocks,
]
const CLIENT_FILTERS = [
  SafFilter.Supplier,
  SafFilter.Periods,
  SafFilter.Feedstocks,
]

export default Tickets

export function useTicketSourcesQuery({
  entity,
  status,
  year,
  search,
  page = 0,
  limit,
  order,
  filters,
}: SafStates) {
  return useMemo<SafQuery>(
    () => ({
      entity_id: entity.id,
      year,
      status,
      search,
      from_idx: page * (limit ?? 0),
      limit: limit || undefined,
      sort_by: order?.column,
      order: order?.direction,
      ...filters,
    }),
    [entity.id, year, status, search, limit, order, filters, page]
  )
}