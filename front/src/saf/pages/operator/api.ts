import { extract } from "carbure/api"
import { EntityPreview } from "carbure/types"
import { CBQUERY_RESET } from "common/hooks/query-builder-2"
import { api, Api, download } from "common/services/api"
import {
  SafFilter,
  SafOperatorQuery,
  SafOperatorSnapshot,
  SafQuery,
  SafTicketDetails,
  SafTicketsResponse,
} from "../../types"
import {
  api as apiFetch,
  download as downloadFetch,
} from "common/services/api-fetch"
import { SafTicketSourceDetails, SafTicketSourcesResponse } from "./types"

export function getOperatorYears(entity_id: number) {
  return apiFetch.GET("/saf/years/", {
    params: {
      query: {
        entity_id,
      },
    },
  })
}

export function getOperatorSnapshot(entity_id: number, year: number) {
  return apiFetch.GET("/saf/snapshot/", {
    params: {
      query: {
        entity_id,
        year,
      },
    },
  })
}

// export function getTicketSourceFilters(field: SafFilter, query: SafQuery) {
//   const params = { filter: field, ...query, ...CBQUERY_RESET }

//   // TO TEST without data
//   // return new Promise<any[]>((resolve) => {
//   //   resolve(data.safClientFilterOptions)
//   // })

//   return api
//     .get<Api<string[]>>("/saf/operator/ticket-sources/filters", { params })
//     .then((res) => res.data.data ?? [])
// }

export function getTicketSourceFilters(
  field: SafFilter,
  query: SafOperatorQuery
) {
  return apiFetch
    .GET("/saf/ticket-sources/filters/", {
      params: {
        query: {
          filter: field,
          ...query,
          ...CBQUERY_RESET,
        },
      },
    })
    .then((res) => res.data ?? [])
}

// export function getOperatorTicketSources(query: SafQuery) {
//   return api.get<Api<SafTicketSourcesResponse>>(
//     "/saf/operator/ticket-sources",
//     { params: query }
//   )
// }
export function getOperatorTicketSources(query: SafOperatorQuery) {
  return apiFetch.GET("/saf/ticket-sources/", {
    params: {
      query,
    },
  })
}

// export function downloadOperatorTicketSources(query: SafQuery) {
//   return download("/saf/operator/ticket-sources", { ...query, export: true })
// }
export function downloadOperatorTicketSources(query: SafOperatorQuery) {
  return downloadFetch("/saf/ticket-sources/export/", {
    ...query,
  })
}

export function getOperatorTicketSourceDetails(
  entity_id: number,
  ticket_source_id: number
) {
  return apiFetch.GET("/saf/ticket-sources/{id}/", {
    params: {
      path: {
        id: ticket_source_id,
      },
      query: {
        entity_id,
      },
    },
  })
}

// export function getOperatorTicketFilters(field: SafFilter, query: SafQuery) {
//   const params = { filter: field, ...query, ...CBQUERY_RESET }
//   return api
//     .get<Api<string[]>>("/saf/operator/tickets/filters", { params })
//     .then((res) => res.data.data ?? [])
// }
export function getOperatorTicketFilters(field: SafFilter, query: SafQuery) {
  return apiFetch
    .GET("/saf/tickets/filters/", {
      params: {
        query: {
          filter: field,
          ...query,
          ...CBQUERY_RESET,
        },
      },
    })
    .then((res) => res.data ?? [])
}

// export function getOperatorTickets(query: SafQuery) {
//   return api.get<Api<SafTicketsResponse>>("/saf/operator/tickets", {
//     params: query,
//   })
// }
export function getOperatorTickets(query: SafQuery) {
  return apiFetch.GET("/saf/tickets/", {
    params: {
      query,
    },
  })
}

export function downloadOperatorTickets(query: SafQuery) {
  return downloadFetch("/saf/tickets/export/", {
    ...query,
  })
}

export function getOperatorTicketDetails(entity_id: number, ticket_id: number) {
  return apiFetch.GET(`/saf/tickets/{id}/`, {
    params: {
      path: {
        id: ticket_id,
      },
      query: {
        entity_id,
      },
    },
  })
}

// export function assignSafTicket(
//   entity_id: number,
//   ticket_source_id: number,
//   volume: number,
//   assignment_period: number,
//   client: EntityPreview,
//   free_field?: string
// ) {
//   return api.post("/saf/operator/assign-ticket", {
//     entity_id,
//     ticket_source_id,
//     assignment_period,
//     volume,
//     client_id: client.id,
//     free_field,
//   })
// }

export function assignSafTicket(
  entity_id: number,
  ticket_source_id: number,
  volume: number,
  assignment_period: number,
  client: EntityPreview,
  free_field?: string
) {
  return apiFetch.POST("/saf/ticket-sources/{id}/assign/", {
    params: {
      path: {
        id: ticket_source_id,
      },
    },
    body: {
      volume,
      assignment_period,
      client_id: client.id,
      free_field,
      agreement_date: "",
      agreement_reference: "",
    },
  })
}

// export function groupedAssignSafTicket(
//   entity_id: number,
//   ticket_sources_ids: number[],
//   volume: number,
//   assignment_period: number,
//   client: EntityPreview,
//   agreement_reference: string,
//   free_field?: string
// ) {
//   return api.post<Api<{ assigned_tickets_count: number }>>(
//     "/saf/operator/grouped-assign-ticket",
//     {
//       entity_id,
//       ticket_sources_ids,
//       assignment_period,
//       volume,
//       client_id: client.id,
//       agreement_reference,
//       free_field,
//     }
//   )
// }
export function groupedAssignSafTicket(
  entity_id: number,
  ticket_sources_ids: number[],
  volume: number,
  assignment_period: number,
  client: EntityPreview,
  agreement_reference: string,
  free_field?: string
) {
  return apiFetch.POST("/saf/ticket-sources/group-assign/", {
    params: {
      query: {
        entity_id,
      },
    },
    body: {
      agreement_date: "",
      agreement_reference: "",
      assignment_period,
      client_id: client.id,
      ticket_sources_ids,
      volume,
      free_field,
    },
  })
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
