import { useLocation } from "react-router-dom"

import useEntity from "carbure/hooks/entity"

import HashRoute from "common/components/hash-route"
import { SearchInput } from "common/components/input"
import Pagination from "common/components/pagination"
import { ActionBar, Bar } from "common/components/scaffold"
import { useQuery } from "common/hooks/async"
import { useQueryParamsStore } from "saf/hooks/query-params-store"
import { useSafQuery } from "saf/hooks/saf-query"
import {
  SafFilter,
  SafOperatorSnapshot,
  SafTicketSource,
  SafTicketSourceStatus,
} from "saf/types"
import LotDetails from "transaction-details/components/lots"
import * as api from "../../api"
import * as data from "../../__test__/data"
import { Filters } from "../filters"
import NoResult from "../no-result"
import { useAutoStatus } from "../operator-tabs"
import { OperatorTicketDetails } from "../ticket-details/operator-details"
import TicketSourceDetail from "../ticket-source-details"
import { StatusSwitcher } from "./status-switcher"
import TicketSourcesTable from "./table"
import { useState } from "react"
import { TicketSourcesSummary } from "./summary"

export interface TicketSourcesProps {
  year: number
  snapshot: SafOperatorSnapshot | undefined
}

export const TicketSources = ({ year, snapshot }: TicketSourcesProps) => {
  const location = useLocation()

  const entity = useEntity()
  const status = useAutoStatus()
  const [state, actions] = useQueryParamsStore(entity, year, status, snapshot)
  console.log("state:", state.selection)
  // const [selection, setSelection] = useState<number[]>([]) //TODO Tous l'object plutot que juste l'id afin d'afficher dans la popup d'affectation

  const query = useSafQuery(state)

  const ticketSourcesResponse = useQuery(api.getOperatorTicketSources, {
    key: "ticket-sources",
    params: [query],
  })

  const ticketSoucesData = ticketSourcesResponse.result?.data.data
  // const ticketSoucesData = data.safTicketSourcesResponse //TO TEST with testing d:ata
  const ids = ticketSoucesData?.ids ?? []

  const total = ticketSoucesData?.total ?? 0
  const count = ticketSoucesData?.returned ?? 0
  const ticketSources = ticketSoucesData?.saf_ticket_sources
  console.log("ticketSources:", ticketSources)

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
            status={status as SafTicketSourceStatus}
          />

          <SearchInput
            asideX
            clear
            debounce={250}
            value={state.search}
            onChange={actions.setSearch}
          />
        </ActionBar>

        {state.selection.length > 0 &&
          status === SafTicketSourceStatus.Available && (
            <TicketSourcesSummary query={query} selection={state.selection} />
          )}

        {count > 0 && ticketSources ? (
          <>
            <TicketSourcesTable
              loading={false}
              order={state.order}
              ticketSources={ticketSources}
              rowLink={showTicketSourceDetail}
              selected={state.selection}
              onSelect={actions.setSelection}
              onOrder={actions.setOrder}
              status={status as SafTicketSourceStatus}
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
            loading={ticketSourcesResponse.loading}
            filters={state.filters}
            onFilter={actions.setFilters}
          />
        )}
      </section>
      <HashRoute
        path="ticket-source/:id"
        element={<TicketSourceDetail neighbors={ids} />}
      />
      <HashRoute path="lot/:id" element={<LotDetails neighbors={[]} />} />
      <HashRoute
        path="ticket/:id"
        element={<OperatorTicketDetails neighbors={[]} />}
      />
    </>
  )
}

const FILTERS = [SafFilter.Clients, SafFilter.Periods, SafFilter.Feedstocks]

export default TicketSources
