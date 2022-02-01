import { Api, api, download } from "common-v2/services/api"
import { Option } from "common-v2/utils/normalize"
import { LotSummary, Snapshot } from "../types"
import { Filter, LotList, LotQuery } from "transactions/types"
import { selectionOrQuery } from "transactions/api"

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
    ...selectionOrQuery(query, selection),
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

export function pinLots(
  entity_id: number,
  selection: number[],
  notify_admin?: boolean,
  notify_auditor?: boolean
) {
  return api.post("/admin/lots/pin", {
    entity_id,
    selection,
    notify_admin,
    notify_auditor,
  })
}

export async function commentLots(
  query: LotQuery,
  selection: number[] | undefined,
  comment: string,
  is_visible_by_admin?: boolean,
  is_visible_by_auditor?: boolean
) {
  if (!comment) return

  return api.post<Api<void>>("/admin/lots/comment", {
    entity_id: query.entity_id,
    selection,
    is_visible_by_admin,
    is_visible_by_auditor,
    comment,
  })
}
