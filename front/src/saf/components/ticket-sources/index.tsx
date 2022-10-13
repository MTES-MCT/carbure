import { useLocation } from "react-router-dom"

import useEntity from "carbure/hooks/entity"

import { ActionBar, Bar } from "common/components/scaffold"
import { useQueryParamsStore } from "saf/hooks/query-params-store"
import {
  SafFilter,
  SafOperatorSnapshot,
  SafQuery,
  SafStates,
  SafTicketSource,
  SafTicketSourceStatus,
} from "saf/types"
import * as api from "../../api"
import { useAutoStatus } from "../operator-tabs"
import { Filters } from "./filters"
import { useMemo } from "react"
import { StatusSwitcher } from "./status-switcher"
import Pagination from "common/components/pagination"
import * as data from "../../__test__/data"
import TicketSourcesTable from "./table"
import { useQuery } from "common/hooks/async"

export interface CertificatesProps {
  year: number
  snapshot: SafOperatorSnapshot | undefined
}

export const TicketSources = ({ year, snapshot }: CertificatesProps) => {
  const location = useLocation()

  const entity = useEntity()
  const status = useAutoStatus()
  const [state, actions] = useQueryParamsStore(entity, year, status, snapshot)
  const query = useTicketSourcesQuery(state)

  const ticketSourcesResponse = useQuery(api.getSafTicketsSources, {
    key: "ticket-sources",
    params: [query],
  })

  const ticketSoucesData = ticketSourcesResponse.result?.data.data
  // const ticketSoucesData = data.safTicketSourcesResponse // TO TEST with testing data
  const total = ticketSoucesData?.total ?? 0
  const count = ticketSoucesData?.returned ?? 0
  const ticketSources = ticketSoucesData?.saf_ticket_sources

  const showTicketSourceDetail = (ticketSource: SafTicketSource) => {
    return {
      pathname: location.pathname,
      search: location.search,
      hash: `ticket-source/${ticketSource.id}`,
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
            status={status}
          />
        </ActionBar>

        {count > 0 && ticketSources && (
          <>
            <TicketSourcesTable
              loading={false}
              order={state.order}
              ticketSources={ticketSources}
              rowLink={showTicketSourceDetail}
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
        )}
      </section>
    </>
  )
}

const FILTERS = [SafFilter.Clients, SafFilter.Feedstocks, SafFilter.Periods]

export default TicketSources

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
      query: search ? search : undefined,
      from_idx: page * (limit ?? 0),
      limit: limit || undefined,
      sort_by: order?.column,
      order: order?.direction,
      ...filters,
    }),
    [entity.id, year, status, search, limit, order, filters, page]
  )
}
