import { extract } from "carbure/api"
import { EntityPreview } from "carbure/types"
import { CBQUERY_RESET } from "common/hooks/query-builder"
import { api, Api, download } from "common/services/api"
import {
  SafFilter,
  SafOperatorSnapshot,
  SafQuery,
  SafTicketDetails,
  SafTicketSourceDetails,
  SafTicketSourcesResponse,
  SafTicketsResponse
} from "../../types"


export function getOperatorYears(entity_id: number) {
  return api.get<Api<number[]>>("/saf/operator/years", {
    params: { entity_id },
  })
}
export function getOperatorSnapshot(entity_id: number, year: number) {
  return api.get<Api<SafOperatorSnapshot>>("/saf/operator/snapshot", {
    params: { entity_id, year },
  })
}

export function getTicketSourceFilters(field: SafFilter, query: SafQuery) {
  const params = { filter: field, ...query, ...CBQUERY_RESET }

  // TO TEST without data
  // return new Promise<any[]>((resolve) => {
  //   resolve(data.safClientFilterOptions)
  // })

  return api
    .get<Api<string[]>>("/saf/operator/ticket-sources/filters", { params })
    .then((res) => res.data.data ?? [])
}

export function getOperatorTicketSources(query: SafQuery) {
  return api.get<Api<SafTicketSourcesResponse>>(
    "/saf/operator/ticket-sources",
    { params: query }
  )
}

export function downloadOperatorTicketSources(query: SafQuery) {
  return download("/saf/operator/ticket-sources", { ...query, export: true })
}

export function getOperatorTicketSourceDetails(
  entity_id: number,
  ticket_source_id: number
) {
  return api.get<Api<SafTicketSourceDetails>>(
    "/saf/operator/ticket-sources/details",
    {
      params: { ticket_source_id, entity_id },
    }
  )
}

export function getOperatorTicketFilters(field: SafFilter, query: SafQuery) {
  const params = { filter: field, ...query, ...CBQUERY_RESET }
  return api
    .get<Api<string[]>>("/saf/operator/tickets/filters", { params })
    .then((res) => res.data.data ?? [])
}

export function getOperatorTickets(query: SafQuery) {
  return api.get<Api<SafTicketsResponse>>("/saf/operator/tickets", {
    params: query,
  })
}

export function downloadOperatorTickets(query: SafQuery) {
  return download("/saf/operator/tickets", { ...query, export: true })
}

export function getOperatorTicketDetails(entity_id: number, ticket_id: number) {
  return api.get<Api<SafTicketDetails>>("/saf/operator/tickets/details", {
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
  return api.post("/saf/operator/assign-ticket", {
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
  return api.post<Api<{ assigned_tickets_count: number }>>(
    "/saf/operator/grouped-assign-ticket",
    {
      entity_id,
      ticket_sources_ids,
      assignment_period,
      volume,
      client_id: client.id,
      agreement_reference,
      free_field,
    }
  )
}

export function cancelSafTicket(entity_id: number, ticket_id: number) {
  return api.post("/saf/operator/cancel-ticket", {
    entity_id,
    ticket_id,
  })
}

export function rejectSafOperatorTicket(
  entity_id: number,
  ticket_id: number,
  comment: string
) {
  return api.post("/saf/operator/reject-ticket", {
    entity_id,
    comment,
    ticket_id,
  })
}

export function creditSafTicketSource(entity_id: number, ticket_id: number) {
  return api.post("/saf/operator/credit-ticket-source", {
    entity_id,
    ticket_id,
  })
}


export async function findClients(entity_id: number, query?: string) {
  return api
    .get<Api<EntityPreview[]>>("/saf/operator/clients", {
      params: { entity_id, query },
    })
    .then(extract)
}
