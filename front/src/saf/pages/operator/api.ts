import { EntityPreview } from "common/types"
import { CBQUERY_RESET } from "common/hooks/query-builder-2"
import { ConsumptionType, SafFilter, SafOperatorQuery } from "../../types"
import {
  api as apiFetch,
  download as downloadFetch,
} from "common/services/api-fetch"
import { ShippingMethodEnum } from "api-schema"

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

export function getOperatorTicketSources(query: SafOperatorQuery) {
  return apiFetch.GET("/saf/ticket-sources/", {
    params: {
      query,
    },
  })
}

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

export function assignSafTicket(
  entity_id: number,
  ticket_source_id: number,
  volume: number,
  assignment_period: number,
  client: EntityPreview,
  i?: string,
  free_field?: string,
  reception_airport?: number,
  shipping_method?: ShippingMethodEnum,
  consumption_type?: ConsumptionType
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
      reception_airport,
      shipping_method,
      consumption_type,
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
  free_field?: string,
  reception_airport?: number,
  shipping_method?: ShippingMethodEnum,
  consumption_type?: ConsumptionType
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
      reception_airport,
      shipping_method,
      consumption_type,
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
  return apiFetch
    .GET("/saf/clients/", {
      params: {
        query: {
          entity_id: `${entity_id}`,
          search: query,
        },
      },
    })
    .then((res) => (res.data ? res.data.results : []))
}
