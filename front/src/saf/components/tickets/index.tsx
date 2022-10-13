import { useLocation } from "react-router-dom"

import useEntity from "carbure/hooks/entity"

import Alert from "common/components/alert"
import { AlertCircle } from "common/components/icons"
import { SearchInput } from "common/components/input"
import Pagination from "common/components/pagination"
import { ActionBar, Bar } from "common/components/scaffold"
import { useQuery } from "common/hooks/async"
import { useMemo } from "react"
import { useTranslation } from "react-i18next"
import { useQueryParamsStore } from "saf/hooks/query-params-store"
import { useSafQuery } from "saf/hooks/saf-query"
import {
  SafFilter,
  SafFilterSelection,
  SafOperatorSnapshot,
  SafQuery,
  SafStates,
  SafTicket,
  SafTicketStatus,
} from "saf/types"
import { ResetButton } from "transactions/components/filters"
import * as api from "../../api"
import * as data from "../../__test__/data"
import { Filters } from "../filters"
import { useAutoStatus } from "../operator-tabs"
import { StatusSwitcher } from "./status-switcher"
import TicketsTable from "./table"

export interface TicketsProps {
  year: number
  snapshot: SafOperatorSnapshot | undefined
}

export const Tickets = ({ year, snapshot }: TicketsProps) => {
  const location = useLocation()

  const entity = useEntity()
  const status = useAutoStatus()
  const [state, actions] = useQueryParamsStore(entity, year, status, snapshot)
  const query = useSafQuery(state)

  const ticketsResponse = useQuery(api.getSafTickets, {
    key: "tickets",
    params: [query],
  })

  const ticketsData = ticketsResponse.result?.data.data
  // const ticketsData = data.safTicketsResponse //TO TEST with testing d:ata
  const total = ticketsData?.total ?? 0
  const count = ticketsData?.returned ?? 0
  const tickets = ticketsData?.saf_tickets

  const showTicketDetail = (ticket: SafTicket) => {
    return {
      pathname: location.pathname,
      search: location.search,
      hash: `tickets/${ticket.id}`,
    }
  }

  return (
    <>
      <Bar>
        <Filters
          filters={FILTERS}
          selected={state.filters}
          onSelect={actions.setFilters}
          getFilterOptions={(filter) =>
            api.getTicketSourceFilters(filter, query)
          }
        />
      </Bar>
      <section>
        <ActionBar>
          <StatusSwitcher
            onSwitch={actions.setStatus}
            count={snapshot}
            status={status as SafTicketStatus}
          />

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
    </>
  )
}

const FILTERS = [SafFilter.Clients, SafFilter.Periods, SafFilter.Feedstocks]

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

export interface FilterManager {
  filters: SafFilterSelection
  onFilter: (filters: SafFilterSelection) => void
}

interface NoResultProps extends Partial<FilterManager> {
  loading?: boolean
}

export const NoResult = ({ loading, filters, onFilter }: NoResultProps) => {
  const { t } = useTranslation()

  return (
    <Alert loading={loading} variant="warning" icon={AlertCircle}>
      <p>{t("Aucun résultat trouvé pour cette recherche")}</p>
      {filters && onFilter && Object.keys(filters).length && (
        <ResetButton filters={filters} onFilter={onFilter} />
      )}
    </Alert>
  )
}
