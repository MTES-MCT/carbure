import { CBQUERY_RESET } from "common/hooks/query-builder-2"
import { api, Api, download } from "common/services/api"
import { api as apiFetch } from "common/services/api-fetch"
import {
  SafClientSnapshot,
  SafFilter,
  SafQuery,
  SafTicketDetails,
  SafTicketsResponse,
} from "../../types"

//AIRLINE

// export function getAirlineYears(entity_id: number) {
//   return api.get<Api<number[]>>("/saf/airline/years", {
//     params: { entity_id },
//   })
// }

// OK
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
  return api.get<Api<SafClientSnapshot>>("/saf/airline/snapshot", {
    params: { entity_id, year },
  })
}

// MISSING TYPE FOR RETURNED DATA
export function getAirlineSnapshot2(entity_id: number, year: number) {
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
  const params = { filter: field, ...query, ...CBQUERY_RESET }
  return api
    .get<Api<string[]>>("/saf/airline/tickets/filters", { params })
    .then((res) => res.data.data ?? [])
}

// Il manque en possibilité d'order des colonnes "supplier"
// Le typage renvoyé par la fonction n'est pas bon, je suis censé récupérer un tableau d'entiers ou de chaines de caractères
// export function getAirlineTicketFilters(field: SafFilter, query: SafQuery) {
//   return apiFetch.GET("/saf/tickets/filters/", {
//     params: {
//       query: {
//         filter: field,
//         ...query,
//         ...CBQUERY_RESET,
//       },
//     },
//   })
// }

// export function getSafAirlineTickets(query: SafQuery) {
//   return api.get<Api<SafTicketsResponse>>("/saf/airline/tickets", {
//     params: query,
//   })
// }

// je récupère bien le nouvel objet de pagination, mais je n'ai plus la liste d'ids dans les résultats
export function getSafAirlineTickets(query: SafQuery) {
  return apiFetch.GET("/saf/tickets/", {
    params: {
      query,
    },
  })
}

export function downloadSafAirlineTickets(query: SafQuery) {
  return download("/saf/airline/tickets", { ...query, export: true })
}

export function getAirlineTicketDetails(entity_id: number, ticket_id: number) {
  return api.get<Api<SafTicketDetails>>("/saf/airline/tickets/details", {
    params: { entity_id, ticket_id },
  })
}

export function acceptSafTicket(entity_id: number, ticket_id: number) {
  return api.post("/saf/airline/accept-ticket", {
    entity_id,
    ticket_id,
  })
}

export function rejectSafAirlineTicket(
  entity_id: number,
  ticket_id: number,
  comment: string
) {
  return api.post("/saf/airline/reject-ticket", {
    entity_id,
    comment,
    ticket_id,
  })
}
