import { extract } from "carbure/api"
import { EntityPreview } from "carbure/types"
import { CBQUERY_RESET } from "common/hooks/query-builder-2"
import { api, Api } from "common/services/api"
import { SafFilter, SafOperatorQuery, SafQuery } from "../../types"
import {
  api as apiFetch,
  download as downloadFetch,
} from "common/services/api-fetch"

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

export function assignSafTicket(
  entity_id: number,
  ticket_source_id: number,
  volume: number,
  assignment_period: number,
  client: EntityPreview,
  i?: string,
  free_field?: string
) {
  return apiFetch.POST("/saf/ticket-sources/{id}/assign/", {
    params: {
      path: {
        id: ticket_source_id,
      },
      query: {
        entity_id,
      },
    },
    body: {
      volume,
      assignment_period,
      client_id: client.id,
      free_field,
      i,
      agreement_date: "",
    },
  })
}

export function groupedAssignSafTicket(
  entity_id: number,
  ticket_sources_ids: number[],
  volume: number,
  assignment_period: number,
  client: EntityPreview,
  i: string,
  free_field?: string
) {
  return apiFetch.POST("/saf/ticket-sources/group-assign/", {
    params: {
      query: {
        entity_id,
      },
    },
    body: {
      i,
      assignment_period,
      client_id: client.id,
      ticket_sources_ids,
      volume,
      free_field,
    },
  })
}

export function cancelSafTicket(entity_id: number, ticket_id: number) {
  return apiFetch.POST("/saf/tickets/{id}/cancel/", {
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

export function rejectSafOperatorTicket(
  entity_id: number,
  ticket_id: number,
  comment: string
) {
  return apiFetch.POST("/saf/tickets/{id}/reject/", {
    params: {
      path: {
        id: ticket_id,
      },
      query: {
        entity_id,
      },
    },
    body: {
      comment,
    },
  })
}

export function creditSafTicketSource(entity_id: number, ticket_id: number) {
  return apiFetch.GET("/saf/tickets/{id}/credit-source/", {
    params: {
      query: {
        entity_id,
      },
      path: {
        id: ticket_id,
      },
    },
  })
}

export async function findClients(entity_id: number, query?: string) {
  return api
    .get<Api<EntityPreview[]>>("/saf/operator/clients", {
      params: { entity_id, query },
    })
    .then(extract)
}
