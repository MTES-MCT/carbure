import { useLocation } from "react-router-dom"

import useEntity from "carbure/hooks/entity"

import { Bar } from "common/components/scaffold"
import { useQueryParamsStore } from "saf/hooks/query-params-store"
import {
  SafFilter,
  SafOperatorSnapshot,
  SafQuery,
  SafStates,
  SafTicketSourceStatus,
} from "saf/types"
import * as api from "../../api"
import { useAutoStatus } from "../operator-tabs"
import { Filters } from "./filters"
import { useMemo } from "react"

export interface CertificatesProps {
  year: number
  snapshot: SafOperatorSnapshot | undefined
}

export const TicketSources = ({ year, snapshot }: CertificatesProps) => {
  // const matomo = useMatomo()
  const location = useLocation()

  const entity = useEntity()
  const status = SafTicketSourceStatus.Available // useAutoStatus()
  const [state, actions] = useQueryParamsStore(entity, year, status, snapshot) // prettier-ignore
  const query = useTicketSourcesQuery(state)

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
