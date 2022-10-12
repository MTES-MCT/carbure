import { api, Api } from "common/services/api"
import {  SafOperatorSnapshot, SafQuery, SafTicketSourceListResponse } from "./types"


// const QUERY_RESET: Partial<Saf> = {
//   limit: undefined,
//   from_idx: undefined,
//   order_by: undefined,
//   direction: undefined,
// }

export function getYears(entity_id: number) {
  return api.get<Api<number[]>>("/years", { params: { entity_id } })
}

export function getSafOperatorSnapshot(entity_id: number, year: number) {
  return api.get<Api<SafOperatorSnapshot>>("/saf-snapshot", {
    params: { entity_id, year },
  })
}

export function getSafTicketsSources(query: SafQuery) {
  return api.get<Api<SafTicketSourceListResponse>>("/saf-tickets-sources", { params: query })
}

// export function getLotFilters(field: SafCertificateFilter, query: SafCertificateQuery) {
//   const params = { field, ...query, ...QUERY_RESET }
//   return api
//     .get<Api<string[]>>("/saf-certificates/filters", { params })
//     .then((res) => res.data.data ?? [])
// }


