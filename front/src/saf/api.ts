import { extract } from "carbure/api"
import { Entity, EntityPreview } from "carbure/types"
import { api, Api } from "common/services/api"
import {
  SafFilter,
  SafOperatorSnapshot,
  SafQuery,
  SafTicketDetails,
  SafTicketSourceDetails,
  SafTicketSourcesResponse,
  SafTicketSourceSummary,
  SafTicketsResponse,
} from "./types"

import * as data from "./__test__/data"
const QUERY_RESET: Partial<SafQuery> = {
  limit: undefined,
  from_idx: undefined,
  order_by: undefined,
  direction: undefined,
}

//AIRLINE

export function getAirlineYears(entity_id: number) {
  return api.get<Api<number[]>>("/v5/saf/airline/years", {
    params: { entity_id },
  })
}

export function getAirlineSnapshot(entity_id: number, year: number) {
  return api.get<Api<SafOperatorSnapshot>>("/v5/saf/airline/snapshot", {
    params: { entity_id, year },
  })
}

export function getAirlineTicketFilters(field: SafFilter, query: SafQuery) {
  const params = { filter: field, ...query, ...QUERY_RESET }
  return api
    .get<Api<string[]>>("/v5/saf/airline/tickets/filters", { params })
    .then((res) => res.data.data ?? [])
}

export function getSafAirlineTickets(query: SafQuery) {
  return api.get<Api<SafTicketsResponse>>("/v5/saf/airline/tickets", {
    params: query,
  })
}

export function getAirlineTicketDetails(entity_id: number, ticket_id: number) {
  return api.get<Api<SafTicketDetails>>("/v5/saf/airline/tickets/details", {
    params: { entity_id, ticket_id },
  })
}

//OPERATOR

export function getOperatorYears(entity_id: number) {
  return api.get<Api<number[]>>("/v5/saf/operator/years", {
    params: { entity_id },
  })
}
export function getOperatorSnapshot(entity_id: number, year: number) {
  return api.get<Api<SafOperatorSnapshot>>("/v5/saf/operator/snapshot", {
    params: { entity_id, year },
  })
}

export function getTicketSourceFilters(field: SafFilter, query: SafQuery) {
  const params = { filter: field, ...query, ...QUERY_RESET }

  // TO TEST without data
  // return new Promise<any[]>((resolve) => {
  //   resolve(data.safClientFilterOptions)
  // })

  return api
    .get<Api<string[]>>("/v5/saf/operator/ticket-sources/filters", { params })
    .then((res) => res.data.data ?? [])
}

export function getOperatorTicketSources(query: SafQuery) {
  return api.get<Api<SafTicketSourcesResponse>>(
    "/v5/saf/operator/ticket-sources",
    { params: query }
  )
}

export function getOperatorTicketSourceDetails(
  entity_id: number,
  ticket_source_id: number
) {
  return api.get<Api<SafTicketSourceDetails>>(
    "/v5/saf/operator/ticket-sources/details",
    {
      params: { ticket_source_id, entity_id },
    }
  )
}

export function getOperatorTicketFilters(field: SafFilter, query: SafQuery) {
  const params = { filter: field, ...query, ...QUERY_RESET }
  return api
    .get<Api<string[]>>("/v5/saf/operator/tickets/filters", { params })
    .then((res) => res.data.data ?? [])
}

export function getOperatorTickets(query: SafQuery) {
  return api.get<Api<SafTicketsResponse>>("/v5/saf/operator/tickets", {
    params: query,
  })
}

export function getOperatorTicketDetails(entity_id: number, ticket_id: number) {
  return api.get<Api<SafTicketDetails>>("/v5/saf/operator/tickets/details", {
    params: { entity_id, ticket_id },
  })
}

export function assignSafTicket(
  entity_id: number,
  ticket_source_id: number,
  volume: number,
  assignment_period: number,
  client: EntityPreview,
  free_field?: string
) {
  return api.post("/v5/saf/operator/assign-ticket", {
    entity_id,
    ticket_source_id,
    assignment_period,
    volume,
    client_id: client.id,
    free_field,
  })
}

export function groupedAssignSafTicket(
  entity_id: number,
  ticket_sources_ids: number[],
  volume: number,
  assignment_period: number,
  client: EntityPreview,
  agreement_reference: string,
  free_field?: string
) {
  return api.post("/v5/saf/operator/grouped-assign-ticket", {
    entity_id,
    ticket_sources_ids,
    assignment_period,
    volume,
    client_id: client.id,
    free_field,
    agreement_reference,
  })
}

export function cancelSafTicket(entity_id: number, ticket_id: number) {
  return api.post("/v5/saf/operator/cancel-ticket", {
    entity_id,
    ticket_id,
  })
}

export function rejectSafTicket(
  entity_id: number,
  ticket_id: number,
  comment: string
) {
  return api.post("/v5/saf/airline/reject-ticket", {
    entity_id,
    comment,
    ticket_id,
  })
}

export function acceptSafTicket(entity_id: number, ticket_id: number) {
  return api.post("/v5/saf/airline/accept-ticket", {
    entity_id,
    ticket_id,
  })
}

export async function findClients(query?: string) {
  return api
    .get<Api<EntityPreview[]>>("/v5/saf/operator/clients", {
      params: { query },
    })
    .then(extract)
}
