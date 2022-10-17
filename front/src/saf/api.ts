import { api, Api } from "common/services/api"
import { SafFilter, SafOperatorSnapshot, SafQuery, SafTicketSourceDetails, SafTicketSourcesResponse, SafTicketsResponse } from "./types"

import * as data from "./__test__/data"
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
  return api.get<Api<SafOperatorSnapshot>>("/saf/snapshot", {
    params: { entity_id, year },
  })
}

export function getSafTicketSources(query: SafQuery) {
  return api.get<Api<SafTicketSourcesResponse>>("/saf/tickets-sources", { params: query })
}

export function getSafTicketSourceDetails(ticket_source_id: number, entity_id: number) {
  return api.get<Api<SafTicketSourceDetails>>("/saf/tickets-sources/", {
    params: { ticket_source_id, entity_id }
  })
}

export function getSafTickets(query: SafQuery) {
  return api.get<Api<SafTicketsResponse>>("/saf/tickets", { params: query })
}

export function getTicketSourceFilters(field: SafFilter, query: SafQuery) {
  const params = { field, ...query, ...QUERY_RESET }

  // TO TEST without data
  return new Promise<any[]>((resolve) => {
    resolve(data.safClientFilterOptions)
  })

  return api
    .get<Api<string[]>>("/saf/tickets-sources/filters", { params })
    .then((res) => res.data.data ?? [])


}


