import { useLocation } from "react-router-dom"

import useEntity from "carbure/hooks/entity"

import HashRoute from "common/components/hash-route"
import { SearchInput } from "common/components/input"
import { ActionBar, Bar } from "common/components/scaffold"
import { useQuery } from "common/hooks/async"
import { useQueryParamsStore } from "saf/hooks/query-params-store"
import { useSafQuery } from "saf/hooks/saf-query"
import {
  SafFilter,
  SafOperatorSnapshot,
  SafQuery,
  SafQueryType,
  SafTicket,
  SafTicketStatus,
} from "saf/types"
import * as api from "../../api"
import { Filters } from "../filters"
import { useAutoStatus } from "../operator-tabs"
import { OperatorTicketDetails } from "../ticket-details/operator-details"
import { StatusSwitcher } from "./status-switcher"
import TicketsTable from "./table"
import TicketSourceDetails from "../ticket-source-details"
import { ExportButton } from "../export"

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
  const [state, actions] = useQueryParamsStore(
    entity,
    year,
    status,
    snapshot,
    type
  )
  const query = useSafQuery(state)
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
        <Filters
          filters={filters}
          selected={state.filters}
          onSelect={actions.setFilters}
          getFilterOptions={getTicketFilter}
        />
      </Bar>
      <section>
        <ActionBar>
          <StatusSwitcher
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
