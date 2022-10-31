import { extract } from "carbure/api"
import { Entity, EntityPreview } from "carbure/types"
import { api, Api } from "common/services/api"
import { SafFilter, SafOperatorSnapshot, SafQuery, SafTicketDetails, SafTicketSourceDetails, SafTicketSourcesResponse, SafTicketsResponse } from "./types"

import * as data from "./__test__/data"
const QUERY_RESET: Partial<SafQuery> = {
  limit: undefined,
  from_idx: undefined,
  order_by: undefined,
  direction: undefined,
}

export function getYears(entity_id: number) {
  return api.get<Api<number[]>>("/v5/saf/years", { params: { entity_id } })
}

export function getSafSnapshot(entity_id: number, year: number) {
  return api.get<Api<SafOperatorSnapshot>>("/v5/saf/snapshot", {
    params: { entity_id, year },
  })
}

export function getSafTicketSources(query: SafQuery) {
  return api.get<Api<SafTicketSourcesResponse>>("/v5/saf/ticket-sources", { params: query })
}

export function getSafTicketSourceDetails(entity_id: number, ticket_source_id: number) {
  return api.get<Api<SafTicketSourceDetails>>("/v5/saf/ticket-sources/details", {
    params: { ticket_source_id, entity_id }
  })
}

export function getSafTickets(query: SafQuery) {
  return api.get<Api<SafTicketsResponse>>("/v5/saf/tickets", { params: query })
}

export function getSafTicketDetails(entity_id: number, ticket_id: number) {
  return api.get<Api<SafTicketDetails>>("/v5/saf/tickets/details", { params: { entity_id, ticket_id } })
}

export function getSafFilters(field: SafFilter, query: SafQuery) {
  const params = { field, ...query, ...QUERY_RESET }

  // TO TEST without data
  return new Promise<any[]>((resolve) => {
    resolve(data.safClientFilterOptions)
  })

  return api
    .get<Api<string[]>>("/v5/saf/tickets-sources/filters", { params })
    .then((res) => res.data.data ?? [])

}

export function assignSafTicket(
  entity_id: number,
  ticket_source_id: number,
  volume: number,
  client: EntityPreview,
  agreement_reference?: string,
  agreement_date?: string,
) {
  return api.post("/v5/saf/assign-ticket", {
    entity_id,
    ticket_source_id,
    volume,
    client_id: client.id,
    agreement_reference,
    agreement_date
  })
}


export function cancelSafTicket(
  entity_id: number,
  ticket_id: number,
) {
  return api.post("/v5/saf/tickets/cancel", {
    entity_id,
    ticket_id
  })
}


export async function findClients(query?: string) {
  return api
    .get<Api<EntityPreview[]>>("/v5/saf/clients", { params: { query } })
    .then(extract)
}