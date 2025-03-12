import { CBQUERY_RESET } from "common/hooks/query-builder-2"
import {
  api as apiFetch,
  download as downloadFetch,
} from "common/services/api-fetch"
import { SafFilter, SafQuery } from "../../types"
import { EtsStatusEnum } from "api-schema"

//AIRLINE

export function getAirlineYears(entity_id: number) {
  return apiFetch.GET("/saf/years/", {
    params: {
      query: {
        entity_id,
      },
    },
  })
}

export function getAirlineSnapshot(entity_id: number, year: number) {
  return apiFetch.GET("/saf/snapshot/", {
    params: {
      query: {
        entity_id,
        year,
      },
    },
  })
}

export function getAirlineTicketFilters(field: SafFilter, query: SafQuery) {
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

export function getSafAirlineTickets(query: SafQuery) {
  return apiFetch.GET("/saf/tickets/", {
    params: {
      query,
    },
  })
}

export function downloadSafAirlineTickets(query: SafQuery) {
  return downloadFetch("/saf/tickets/export/", {
    ...query,
  })
}

export function getAirlineTicketDetails(entity_id: number, ticket_id: number) {
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

export function acceptSafTicket(
  entity_id: number,
  ticket_id: number,
  ets_status: EtsStatusEnum
) {
  return apiFetch.POST("/saf/tickets/{id}/accept/", {
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

export function rejectSafAirlineTicket(
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
