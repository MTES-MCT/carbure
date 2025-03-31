import { useLocation } from "react-router-dom"

import useEntity from "common/hooks/entity"

import HashRoute from "common/components/hash-route"
import { SearchInput } from "common/components/input"
import { ActionBar, Content } from "common/components/scaffold"
import { useQuery } from "common/hooks/async"
import {
  SafColumsOrder,
  SafFilter,
  SafOperatorSnapshot,
  SafQuery,
  SafQueryType,
  SafTicket,
  SafTicketStatus,
} from "saf/types"
import { getTicketFilters, getTickets, downloadTickets } from "saf/api"
import { SafFilters } from "saf/components/filters"
import { useAutoStatus } from "./index.hooks"
import OperatorTicketDetails from "../../components/ticket-details"
import { SafStatusSwitcher } from "./status-switcher"
import TicketsTable from "saf/components/tickets/table"
import TicketSourceDetails from "../../components/ticket-source-details"
import {
  useCBQueryBuilder,
  useCBQueryParamsStore,
} from "common/hooks/query-builder-2"
import { useTranslation } from "react-i18next"
import { usePrivateNavigation } from "common/layouts/navigation"
import { ExportButton } from "saf/components/export"
import { RecapQuantity } from "common/molecules/recap-quantity"
import { formatUnit } from "common/utils/formatters"
import { Unit } from "common/types"

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
  const { t } = useTranslation()
  usePrivateNavigation(
    type === "received" ? t("Tickets reçus") : t("Tickets affectés")
  )

  const location = useLocation()

  const entity = useEntity()
  const status = useAutoStatus()
  const [state, actions] = useCBQueryParamsStore(entity, year, status, type)
  const query = useCBQueryBuilder<
    SafColumsOrder[],
    SafTicketStatus,
    SafQueryType
  >(state)
  const apiGetTickets = (query: SafQuery) => getTickets(query)

  const ticketsResponse = useQuery(apiGetTickets, {
    key: "tickets",
    params: [query],
  })

  const ticketsData = ticketsResponse.result?.data
  const ids = ticketsData?.results.map((ticket) => ticket.id) || []

  const showTicketDetail = (ticket: SafTicket) => {
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
  const filters =
    type === "received"
      ? OPERATOR_RECEIVED_FILTERS //
      : OPERATOR_ASSIGNED_FILTERS

  return (
    <>
      <SafStatusSwitcher
        onSwitch={actions.setStatus}
        type={type}
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
            <OperatorTicketDetails
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

const OPERATOR_RECEIVED_FILTERS = [
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
