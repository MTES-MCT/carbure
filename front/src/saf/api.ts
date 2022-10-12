import { api, Api } from "common/services/api"
import { SafFilter, SafOperatorSnapshot, SafQuery, SafTicketSourcesResponse } from "./types"


const QUERY_RESET: Partial<SafQuery> = {
  limit: undefined,
  from_idx: undefined,
  order_by: undefined,
  direction: undefined,
}

export function getYears(entity_id: number) {
  return api.get<Api<number[]>>("/years", { params: { entity_id } })
}

export function getSafOperatorSnapshot(entity_id: number, year: number) {
  return api.get<Api<SafOperatorSnapshot>>("/saf-snapshot", {
    params: { entity_id, year },
  })
}

export function getSafTicketsSources(query: SafQuery) {
  return api.get<Api<SafTicketSourcesResponse>>("/saf-tickets-sources", { params: query })
}

export function getTicketSourceFilters(field: SafFilter, query: SafQuery) {
  const params = { field, ...query, ...QUERY_RESET }
  // params.field = filter
  return api
    .get<Api<string[]>>("/saf-tickets-sources/filters", { params })
    .then((res) => res.data.data ?? [])
}


