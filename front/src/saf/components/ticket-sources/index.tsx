import { useLocation } from "react-router-dom"

import useEntity from "carbure/hooks/entity"

import { ActionBar, Bar } from "common/components/scaffold"
import { useQueryParamsStore } from "saf/hooks/query-params-store"
import {
  SafFilter,
  SafFilterSelection,
  SafOperatorSnapshot,
  SafQuery,
  SafStates,
  SafTicketSource,
  SafTicketSourceStatus,
} from "saf/types"
import * as api from "../../api"
import { useAutoStatus } from "../operator-tabs"
import { Filters } from "../filters"
import { useMemo } from "react"
import { StatusSwitcher } from "./status-switcher"
import Pagination from "common/components/pagination"
import * as data from "../../__test__/data"
import TicketSourcesTable from "./table"
import { useQuery } from "common/hooks/async"
import { AlertCircle } from "common/components/icons"
import Alert from "common/components/alert"
import { ResetButton } from "transactions/components/filters"
import { useTranslation } from "react-i18next"
import { SearchInput } from "common/components/input"
import { useSafQuery } from "saf/hooks/saf-query"
import HashRoute from "common/components/hash-route"
import TicketSourceDetail from "../ticket-source-details"
import NoResult from "../no-result"
import LotDetails from "transaction-details/components/lots"
import TicketDetails from "../ticket-details"

export interface TicketSourcesProps {
  year: number
  snapshot: SafOperatorSnapshot | undefined
}

export const TicketSources = ({ year, snapshot }: TicketSourcesProps) => {
  const location = useLocation()

  const entity = useEntity()
  const status = useAutoStatus()
  const [state, actions] = useQueryParamsStore(entity, year, status, snapshot)
  const query = useSafQuery(state)

  const ticketSourcesResponse = useQuery(api.getSafTicketSources, {
    key: "ticket-sources",
    params: [query],
  })

  const ticketSoucesData = ticketSourcesResponse.result?.data.data
  // const ticketSoucesData = data.safTicketSourcesResponse //TO TEST with testing d:ata
  const ids = ticketSoucesData?.ids ?? []

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

        {count > 0 && ticketSources ? (
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
      <HashRoute path="ticket/:id" element={<TicketDetails neighbors={[]} />} />
    </>
  )
}

const FILTERS = [SafFilter.Clients, SafFilter.Periods, SafFilter.Feedstocks]

export default TicketSources
