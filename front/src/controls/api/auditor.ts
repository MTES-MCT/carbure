import { Api, api, download } from "common/services/api"
import { Option } from "common/utils/normalize"
import { LotSummary, Snapshot } from "../types"
import {
  Filter,
  LotList,
  LotQuery,
  StockList,
  StockQuery,
  StockSummary,
} from "transactions/types"
import { selectionOrQuery } from "transactions/api"

const QUERY_RESET: Partial<LotQuery> = {
  limit: undefined,
  from_idx: undefined,
  order_by: undefined,
  direction: undefined,
}

export function getYears(entity_id: number) {
  return api.get<Api<number[]>>("/v5/audit/years", { params: { entity_id } })
}

export function getSnapshot(entity_id: number, year: number) {
  return api.get<Api<Snapshot>>("/v5/audit/snapshot", {
    params: { entity_id, year },
  })
}

export function getLots(query: LotQuery) {
  return api.get<Api<LotList>>("/v5/audit/lots", { params: query })
}

export function getStocks(query: StockQuery) {
  return api.get<Api<StockList>>("/v5/audit/stocks", { params: query })
}

export function downloadLots(query: LotQuery, selection: number[]) {
  return download("/v5/audit/lots", {
    ...selectionOrQuery(
      { ...query, from_idx: undefined, limit: undefined },
      selection
    ),
    export: true,
  })
}

export function getLotsSummary(
  query: LotQuery,
  selection: number[],
  short?: boolean
) {
  return api.get<Api<LotSummary>>("/v5/audit/lots/summary", {
    params: { ...query, selection, ...QUERY_RESET, short },
  })
}

export function getStocksSummary(
  query: StockQuery,
  selection: number[],
  short?: boolean
) {
  return api.get<Api<StockSummary>>("/v5/audit/stocks/summary", {
    params: { ...query, selection, ...QUERY_RESET, short },
  })
}

export function getLotFilters(field: Filter, query: LotQuery) {
  const params = { field, ...query, ...QUERY_RESET }
  return api
    .get<Api<Option[]>>("/v5/audit/lots/filters", { params })
    .then((res) => res.data.data ?? [])
}

export function getStockFilters(field: Filter, query: StockQuery) {
  const params = { field, ...query, ...QUERY_RESET }
  return api
    .get<Api<Option[]>>("/v5/audit/stocks/filters", { params })
    .then((res) => res.data.data ?? [])
}

export function pinLots(
  entity_id: number,
  selection: number[],
  notify_admin?: boolean,
  notify_auditor?: boolean
) {
  return api.post("/v5/audit/lots/pin", {
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

  return api.post<Api<void>>("/v5/audit/lots/comment", {
    entity_id: query.entity_id,
    selection,
    is_visible_by_admin,
    is_visible_by_auditor,
    comment,
  })
}

export async function markAsConform(entity_id: number, selection: number[]) {
  return api.post<Api<void>>("/v5/audit/lots/mark-as-conform", {
    entity_id,
    selection,
  })
}

export async function markAsNonConform(entity_id: number, selection: number[]) {
  return api.post<Api<void>>("/v5/audit/lots/mark-as-nonconform", {
    entity_id,
    selection,
  })
}
