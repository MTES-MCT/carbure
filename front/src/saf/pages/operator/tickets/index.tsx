import { useLocation } from "react-router-dom"

import useEntity from "carbure/hooks/entity"

import HashRoute from "common/components/hash-route"
import { SearchInput } from "common/components/input"
import { ActionBar, Bar } from "common/components/scaffold"
import { useQuery } from "common/hooks/async"
import {
  SafFilter,
  SafOperatorSnapshot,
  SafQuery,
  SafQueryType,
  SafStates,
  SafTicket,
  SafTicketStatus,
} from "saf/types"
import * as api from "../api"
import { SafFilters } from "../../../components/filters"
import { useAutoStatus } from "../tabs"
import { OperatorTicketDetails } from "../ticket-details"
import { SafStatusSwitcher } from "./status-switcher"
import TicketsTable from "../../../components/tickets/table"
import TicketSourceDetails from "../ticket-source-details"
import { ExportButton } from "../ticket-source-details/export"
import {
  useCBQueryBuilder,
  useCBQueryParamsStore,
} from "common/hooks/query-builder"

export interface OperatorTicketsProps {
  type: SafQueryType
  year: number
  snapshot?: SafOperatorSnapshot
}

export const OperatorTickets = ({
  type,
  year,
  snapshot,
}: OperatorTicketsProps) => {
  const location = useLocation()

  const entity = useEntity()
  const status = useAutoStatus()
  const [state, actions] = useCBQueryParamsStore<SafStates>(
    entity,
    year,
    status,
    snapshot,
    type
  )
  const query = useCBQueryBuilder(state)
  const apiGetTickets = (query: SafQuery) => api.getOperatorTickets(query)

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

  const getTicketFilter = (filter: any) =>
    api.getOperatorTicketFilters(filter, query)

  const filters =
    type === "received"
      ? OPERATOR_RECEIVED_FILTERS //
      : OPERATOR_ASSIGNED_FILTERS

  return (
    <>
      <Bar>
        <SafFilters
          filters={filters}
          selected={state.filters}
          onSelect={actions.setFilters}
          getFilterOptions={getTicketFilter}
        />
      </Bar>
      <section>
        <ActionBar>
          <SafStatusSwitcher
            onSwitch={actions.setStatus}
            type={type}
            count={snapshot as SafOperatorSnapshot}
            status={status as SafTicketStatus}
          />

          <ExportButton
            asideX
            query={query}
            download={api.downloadOperatorTickets}
          />
          <SearchInput
            clear
            debounce={250}
            value={state.search}
            onChange={actions.setSearch}
          />
        </ActionBar>

        <TicketsTable
          loading={ticketsResponse.loading}
          state={state}
          actions={actions}
          order={state.order}
          status={status as SafTicketStatus}
          ticketsData={ticketsData}
          client={type === "received"}
          rowLink={showTicketDetail}
        />
      </section>

      <HashRoute
        path="ticket/:id"
        element={<OperatorTicketDetails neighbors={ids} />}
      />
      <HashRoute path="ticket-source/:id" element={<TicketSourceDetails />} />
    </>
  )
}

const OPERATOR_RECEIVED_FILTERS = [
  SafFilter.Suppliers,
  SafFilter.Periods,
  SafFilter.Feedstocks,
  SafFilter.CountriesOfOrigin,
  SafFilter.ProductionSites,
]

const OPERATOR_ASSIGNED_FILTERS = [
  SafFilter.Clients,
  SafFilter.Periods,
  SafFilter.Feedstocks,
  SafFilter.CountriesOfOrigin,
  SafFilter.ProductionSites,
]

export default OperatorTickets
