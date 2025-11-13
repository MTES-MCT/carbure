import { useLocation } from "react-router-dom"

import useEntity from "common/hooks/entity"

import HashRoute from "common/components/hash-route"
import { SearchInput } from "common/components/inputs2"
import { ActionBar, Content } from "common/components/scaffold"
import { useQuery } from "common/hooks/async"
import {
  SafFilter,
  SafSnapshot,
  SafTicketQuery,
  SafTicketType,
  SafTicketPreview,
} from "saf/types"
import { getTicketFilters, getTickets, downloadTickets } from "saf/api"
import { SafFilters } from "saf/components/filters"
import { useAutoStatus, useSafTicketsQueryBuilder } from "./index.hooks"
import { TicketDetails } from "saf/pages/ticket-details"
import { StatusSwitcher } from "./components/status-switcher"
import TicketsTable from "saf/pages/tickets/components/table"
import { TicketSourceDetails } from "saf/pages/ticket-source-details"

import { useTranslation } from "react-i18next"
import { usePrivateNavigation } from "common/layouts/navigation"
import { ExportButton } from "common/components/export"
import { RecapQuantity } from "common/molecules/recap-quantity"
import { formatUnit } from "common/utils/formatters"
import { Unit } from "common/types"

export interface TicketsProps {
  type: SafTicketType
  year: number
  snapshot?: SafSnapshot
}

export const SafTickets = ({ type, year, snapshot }: TicketsProps) => {
  const { t } = useTranslation()
  usePrivateNavigation(
    type === "received" ? t("Tickets reçus") : t("Tickets affectés")
  )

  const location = useLocation()

  const entity = useEntity()
  const status = useAutoStatus()
  // const [state, actions] = useCBQueryParamsStore(entity, year, status, type)
  // const query = useCBQueryBuilder<
  //   SafTicketOrder[],
  //   SafTicketStatus,
  //   SafTicketType
  // >(state)
  const { query, state, actions } = useSafTicketsQueryBuilder({ type, year })
  const apiGetTickets = (query: SafTicketQuery) => getTickets(query)

  const ticketsResponse = useQuery(apiGetTickets, {
    key: "tickets",
    params: [query],
  })

  const ticketsData = ticketsResponse.result?.data
  const ids = ticketsData?.results.map((ticket) => ticket.id) || []

  const showTicketDetail = (ticket: SafTicketPreview) => {
    return {
      pathname: location.pathname,
      search: location.search,
      hash: `ticket/${ticket.id}`,
    }
  }

  const getTicketFilter = (filter: SafFilter) => getTicketFilters(filter, query)

  const fetchIdsForPage = async (page: number) => {
    const response = await apiGetTickets({
      ...query,
      page,
    })

    return response.data?.results ?? []
  }

  const isAdmin = entity.isAdmin || entity.isExternal

  let filters: SafFilter[] = []
  if (isAdmin) filters = ADMIN_FILTERS
  else if (type === "received") filters = RECEIVED_FILTERS
  else if (type === "assigned") filters = ASSIGNED_FILTERS

  return (
    <>
      <StatusSwitcher
        onSwitch={actions.setStatus}
        type={type}
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
          <ExportButton query={query} download={downloadTickets} />
        </ActionBar>

        <SafFilters
          filters={filters}
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
          loading={ticketsResponse.loading}
          state={state}
          actions={actions}
          order={state.order}
          status={status}
          ticketsData={ticketsData}
          client={type === "received"}
          rowLink={showTicketDetail}
        />

        <HashRoute
          path="ticket/:id"
          element={
            <TicketDetails
              limit={state.limit}
              total={ticketsData?.count ?? 0}
              fetchIdsForPage={fetchIdsForPage}
              baseIdsList={ids}
            />
          }
        />
        <HashRoute path="ticket-source/:id" element={<TicketSourceDetails />} />
      </Content>
    </>
  )
}

const TICKET_FILTERS = [
  SafFilter.Periods,
  SafFilter.Feedstocks,
  SafFilter.CountriesOfOrigin,
  SafFilter.ProductionSites,
  SafFilter.ConsumptionTypes,
  SafFilter.Airport,
]

const RECEIVED_FILTERS = [
  SafFilter.Suppliers, //
  ...TICKET_FILTERS,
]

const ASSIGNED_FILTERS = [
  SafFilter.Clients, //
  ...TICKET_FILTERS,
]

const ADMIN_FILTERS = [
  SafFilter.Suppliers,
  SafFilter.Clients,
  ...TICKET_FILTERS,
]
