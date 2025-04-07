import { useLocation } from "react-router-dom"

import useEntity from "common/hooks/entity"

import HashRoute from "common/components/hash-route"
import { ActionBar } from "common/components/scaffold"
import { useQuery } from "common/hooks/async"
import {
  SafColumsOrder,
  SafFilter,
  SafQuery,
  SafTicket,
  SafTicketStatus,
} from "saf/types"
import { getTicketFilters, getTickets, downloadTickets } from "saf/api"
import { SafFilters } from "saf/components/filters"
import { useAutoStatus } from "./tickets.hooks"
import ClientTicketDetails from "./ticket-details"
import TicketsTable from "saf/components/tickets/table"
import {
  useCBQueryBuilder,
  useCBQueryParamsStore,
} from "common/hooks/query-builder-2"
import { SearchInput } from "common/components/inputs2"
import { ExportButton } from "saf/components/export"
import { RecapQuantity } from "common/molecules/recap-quantity"
import { formatUnit } from "common/utils/formatters"
import { Unit } from "common/types"
import { useTranslation } from "react-i18next"

export interface AirlineTicketsProps {
  year: number
}

export const AirlineTickets = ({ year }: AirlineTicketsProps) => {
  const location = useLocation()
  const { t } = useTranslation()
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
    return getTickets(query)
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
    return getTicketFilters(filter, query)
  }

  return (
    <>
      <ActionBar>
        <ActionBar.Grow>
          <SearchInput
            debounce={250}
            value={state.search}
            onChange={actions.setSearch}
          />
        </ActionBar.Grow>

        <ExportButton query={query} download={downloadTickets} />
      </ActionBar>

      <SafFilters
        filters={CLIENT_FILTERS}
        selected={state.filters}
        onSelect={actions.setFilters}
        getFilterOptions={getTicketFilter}
      />

      <RecapQuantity
        text={t("{{count}} volumes pour un total de {{total}}", {
          count: ticketsData?.count,
          total: formatUnit(ticketsData?.total_volume ?? 0, Unit.l),
        })}
      />

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
  SafFilter.Periods,
  SafFilter.Feedstocks,
  SafFilter.ConsumptionTypes,
]

export default AirlineTickets
