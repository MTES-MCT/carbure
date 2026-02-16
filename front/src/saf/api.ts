import { api, download } from "common/services/api-fetch"
import { EntityPreview } from "common/types"
import {
  SafTicketQuery,
  ConsumptionType,
  SafTicketSourceQuery,
  SafShippingMethod,
  SafFilter,
  SafTicketFilter,
  SafTicketSourceFilter,
} from "./types"
import { QUERY_RESET } from "common/hooks/query-builder-2"
import { EtsStatusEnum } from "api-schema"

export function getYears(entity_id: number) {
  return api.GET("/saf/years/", {
    params: {
      query: {
        entity_id,
      },
    },
  })
}

export function getSnapshot(entity_id: number, year: number) {
  return api.GET("/saf/snapshot/", {
    params: {
      query: {
        entity_id,
        year,
      },
    },
  })
}

export function getTicketFilters(field: SafFilter, query: SafTicketQuery) {
  return api
    .GET("/saf/tickets/filters/", {
      params: {
        query: {
          filter: field as unknown as SafTicketFilter,
          ...query,
          ...QUERY_RESET,
        },
      },
    })
    .then((res) => res.data ?? [])
}

export function getTickets(query: SafTicketQuery) {
  return api.GET("/saf/tickets/", {
    params: { query },
  })
}

export function downloadTickets(query: SafTicketQuery) {
  return download("/saf/tickets/export/", {
    ...query,
  })
}

export function getTicketDetails(entity_id: number, ticket_id: number) {
  return api.GET(`/saf/tickets/{id}/`, {
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

export function rejectTicket(
  entity_id: number,
  ticket_id: number,
  comment: string
) {
  return api.POST("/saf/tickets/{id}/reject/", {
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

export function acceptTicket(
  entity_id: number,
  ticket_id: number,
  ets_status: EtsStatusEnum
) {
  return api.POST("/saf/tickets/{id}/accept/", {
    params: {
      path: {
        id: ticket_id,
      },
      query: {
        entity_id,
      },
    },
    body: {
      ets_status,
    },
  })
}

export function getTicketSourceFilters(
  field: SafFilter,
  query: SafTicketSourceQuery
) {
  return api
    .GET("/saf/ticket-sources/filters/", {
      params: {
        query: {
          filter: field as unknown as SafTicketSourceFilter,
          ...query,
          ...QUERY_RESET,
        },
      },
    })
    .then((res) => res.data ?? [])
}

export function getOperatorTicketSources(query: SafTicketSourceQuery) {
  return api.GET("/saf/ticket-sources/", {
    params: {
      query,
    },
  })
}

export function downloadOperatorTicketSources(query: SafTicketSourceQuery) {
  return download("/saf/ticket-sources/export/", {
    ...query,
  })
}

export function getOperatorTicketSourceDetails(
  entity_id: number,
  ticket_source_id: number
) {
  return api.GET("/saf/ticket-sources/{id}/", {
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
  shipping_method?: SafShippingMethod,
  has_intermediary_depot?: boolean,
  consumption_type?: ConsumptionType,
  pos_number?: string
) {
  return api.POST("/saf/ticket-sources/{id}/assign/", {
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
      has_intermediary_depot: has_intermediary_depot ?? false,
      consumption_type,
      pos_number,
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
  shipping_method?: SafShippingMethod,
  has_intermediary_depot?: boolean,
  consumption_type?: ConsumptionType
) {
  return api.POST("/saf/ticket-sources/group-assign/", {
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
      has_intermediary_depot: has_intermediary_depot ?? false,
      consumption_type,
    },
  })
}

export function cancelSafTicket(entity_id: number, ticket_id: number) {
  return api.POST("/saf/tickets/{id}/cancel/", {
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
  return api.POST("/saf/tickets/{id}/credit-source/", {
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

export async function findAirports(
  query?: string,
  public_only?: boolean,
  origin_depot_id?: number,
  shipping_method?: SafShippingMethod,
  has_intermediary_depot?: boolean
) {
  const res = await api.GET("/resources/airports", {
    params: {
      query: {
        query,
        public_only,
        origin_depot_id,
        shipping_method,
        has_intermediary_depot,
      },
    },
  })

  return res.data ?? []
}
