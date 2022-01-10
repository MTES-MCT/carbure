import { Api, api, download } from "common-v2/services/api"
import { Option } from "common-v2/utils/normalize"
import { LotSummary, Snapshot } from "./types"
import { Filter, LotList, LotQuery } from "transactions/types"

const QUERY_RESET: Partial<LotQuery> = {
  limit: undefined,
  from_idx: undefined,
  order_by: undefined,
  direction: undefined,
}

export function getYears(entity_id: number) {
  return api.get<Api<number[]>>("/admin/years", { params: { entity_id } })
}

export function getSnapshot(entity_id: number, year: number) {
  return api.get<Api<Snapshot>>("/admin/snapshot", {
    params: { entity_id, year },
  })
}

// ENDPOINTS FOR LOTS

export function getLots(query: LotQuery) {
  return api.get<Api<LotList>>("/admin/lots", { params: query })
}

export function downloadLots(query: LotQuery, selection: number[]) {
  return download("/admin/lots", {
    ...getParams(query, selection),
    export: true,
  })
}

export function getLotsSummary(
  query: LotQuery,
  selection: number[],
  short?: boolean
) {
  return api.get<Api<LotSummary>>("/admin/lots/summary", {
    params: { ...query, selection, ...QUERY_RESET, short },
  })
}

export function getLotFilters(field: Filter, query: LotQuery) {
  const params = { field, ...query, ...QUERY_RESET }
  return api
    .get<Api<Option[]>>("/admin/lots/filters", { params })
    .then((res) => res.data.data ?? [])
}

export async function commentLots(
  query: LotQuery,
  selection: number[] | undefined,
  comment: string
) {
  if (!comment) return

  return api.post<Api<void>>("/admin/lots/comment", {
    ...getParams(query, selection),
    comment,
  })
}

export function getParams(query: LotQuery, selection?: number[]) {
  if (!selection || selection.length === 0) return query
  else return { entity_id: query.entity_id, selection }
}
