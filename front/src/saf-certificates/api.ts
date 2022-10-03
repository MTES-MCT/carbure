import { api, Api } from "common/services/api"
import { SafCertificateFilter, SafCertificateListResponse, SafCertificateQuery, SafSnapshot } from "./types"


const QUERY_RESET: Partial<SafCertificateQuery> = {
  limit: undefined,
  from_idx: undefined,
  order_by: undefined,
  direction: undefined,
}

export function getYears(entity_id: number) {
  return api.get<Api<number[]>>("/years", { params: { entity_id } })
}

export function getSafSnapshot(entity_id: number, year: number) {
  return api.get<Api<SafSnapshot>>("/saf-snapshot", {
    params: { entity_id, year },
  })
}

export function getSafCertificates(query: SafCertificateQuery) {
  return api.get<Api<SafCertificateListResponse>>("/saf-certificates", { params: query })
}

export function getLotFilters(field: SafCertificateFilter, query: SafCertificateQuery) {
  const params = { field, ...query, ...QUERY_RESET }
  return api
    .get<Api<string[]>>("/saf-certificates/filters", { params })
    .then((res) => res.data.data ?? [])
}


