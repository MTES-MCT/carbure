import { api, Api } from "common-v2/services/api"
import { Option } from "common-v2/utils/normalize"
import {
  LotList,
  LotQuery,
  StockQuery,
  Snapshot,
  Filter,
  StockList,
  LotSummary,
  DeclarationSummary,
  StockSummary,
} from "./types"

const QUERY_RESET: Partial<LotQuery> = {
  limit: undefined,
  from_idx: undefined,
  order_by: undefined,
  direction: undefined,
}

export function getYears(entity_id: number) {
  return api.get<Api<number[]>>("/years", { params: { entity_id } })
}

export function getSnapshot(entity_id: number, year: number) {
  return api.get<Api<Snapshot>>("/snapshot", {
    params: { entity_id, year },
  })
}

// ENDPOINTS FOR LOTS

export function getLots(query: LotQuery) {
  return api.get<Api<LotList>>("/lots", { params: query })
}

export function importLots(entity_id: number, file: File) {
  return api.post<Api<void>>("/lots/add-excel", { entity_id, file })
}

export function downloadLots(query: LotQuery, selection: number[]) {
  return null
}

export function getLotsSummary(
  query: LotQuery,
  selection: number[],
  short?: boolean
) {
  return api.get<Api<LotSummary>>("/lots/summary", {
    params: { ...query, selection, ...QUERY_RESET, short },
  })
}

export function getDeclarations(entity_id: number, year: number) {
  return api.get<Api<DeclarationSummary[]>>("/declarations", {
    params: { entity_id, year },
  })
}

export function getLotFilters(field: Filter, query: LotQuery) {
  const params = { field, ...query, ...QUERY_RESET }
  return api
    .get<Api<Option[]>>("/lots/filters", { params })
    .then((res) => res.data.data ?? [])
}

export function sendLots(query: LotQuery, selection?: number[]) {
  return api.post<Api<void>>("/lots/send", getParams(query, selection))
}

export function deleteLots(query: LotQuery, selection?: number[]) {
  return api.post<Api<void>>("/lots/delete", getParams(query, selection))
}

export function rejectLots(query: LotQuery, selection?: number[]) {
  return api.post<Api<void>>("/lots/reject", getParams(query, selection))
}

export function getParams(query: LotQuery, selection?: number[]) {
  if (!selection || selection.length === 0) return query
  else return { entity_id: query.entity_id, selection }
}

// ENDPOINTS FOR STOCKS

export function getStocks(query: StockQuery) {
  return api.get<Api<StockList>>("/stocks", { params: query })
}

export function getStockSummary(
  query: StockQuery,
  selection: number[],
  short?: boolean
) {
  return api.get<Api<StockSummary>>("/stocks/summary", {
    params: { ...query, selection, ...QUERY_RESET, short },
  })
}

export function getStockFilters(field: Filter, query: LotQuery) {
  const params = { field, ...query, ...QUERY_RESET }
  return api
    .get<Api<Option[]>>("/stocks/filters", { params })
    .then((res) => res.data.data ?? [])
}
