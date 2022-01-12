import { Entity } from "carbure/types"
import { api, Api, download } from "common-v2/services/api"
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
  StockPayload,
  TransformETBEPayload
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
  return download("/lots", { ...getParams(query, selection), export: true })
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

export function validateDeclaration(entity_id: number, period: number) {
  return api.post<Api<void>>("/declarations/validate", { entity_id, period })
}

export function invalidateDeclaration(entity_id: number, period: number) {
  return api.post<Api<void>>("/declarations/invalidate", { entity_id, period })
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

export function acceptReleaseForConsumption(
  query: LotQuery,
  selection?: number[]
) {
  return api.post<Api<void>>(
    "/lots/accept-release-for-consumption",
    getParams(query, selection)
  )
}

export function acceptInStock(query: LotQuery, selection?: number[]) {
  return api.post<Api<void>>(
    "/lots/accept-in-stock",
    getParams(query, selection)
  )
}

export function acceptForTrading(
  query: LotQuery,
  selection: number[] | undefined,
  client: Entity | string,
  certificate: string
) {
  const params =
    client instanceof Object
      ? { client_entity_id: client.id }
      : { unknown_client: client }

  return api.post<Api<void>>("/lots/accept-trading", {
    ...getParams(query, selection),
    ...params,
    certificate,
  })
}

export function acceptForProcessing(
  query: LotQuery,
  selection: number[] | undefined,
  processing_entity_id: number
) {
  return api.post<Api<void>>("/lots/accept-processing", {
    ...getParams(query, selection),
    processing_entity_id,
  })
}

export function acceptForBlending(
  query: LotQuery,
  selection: number[] | undefined
) {
  return api.post<Api<void>>(
    "/lots/accept-blending",
    getParams(query, selection)
  )
}
export function acceptForExport(
  query: LotQuery,
  selection: number[] | undefined
) {
  return api.post<Api<void>>("/lots/accept-export", getParams(query, selection))
}

export function deleteLots(query: LotQuery, selection?: number[]) {
  return api.post<Api<void>>("/lots/delete", getParams(query, selection))
}

export function rejectLots(query: LotQuery, selection?: number[]) {
  return api.post<Api<void>>("/lots/reject", getParams(query, selection))
}

export function requestFix(entity_id: number, lot_ids: number[]) {
  return api.post<Api<void>>("/lots/request-fix", { entity_id, lot_ids })
}

export function markAsFixed(entity_id: number, lot_ids: number[]) {
  return api.post<Api<void>>("/lots/mark-as-fixed", { entity_id, lot_ids })
}

export function approveFix(entity_id: number, lot_ids: number[]) {
  return api.post<Api<void>>("/lots/approve-fix", { entity_id, lot_ids })
}

export function recallLots(entity_id: number, lot_ids: number[]) {
  return api.post<Api<void>>("/lots/recall", { entity_id, lot_ids })
}

export async function commentLots(
  query: LotQuery,
  selection: number[] | undefined,
  comment: string
) {
  if (!comment) return

  return api.post<Api<void>>("/lots/comment", {
    ...getParams(query, selection),
    comment,
  })
}

export function getParams(query: LotQuery, selection?: number[]) {
  if (!selection || selection.length === 0) return query
  else return { entity_id: query.entity_id, selection }
}

// ENDPOINTS FOR STOCKS

export function getStocks(query: StockQuery) {
  return api.get<Api<StockList>>("/stocks", { params: query })
}

export function downloadStocks(query: StockQuery, selection: number[]) {
  return download("/stocks", { ...getParams(query, selection), export: true })
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

export function getStockFilters(field: Filter, query: StockQuery) {
  const params = { field, ...query, ...QUERY_RESET }
  return api
    .get<Api<Option[]>>("/stocks/filters", { params })
    .then((res) => res.data.data ?? [])
}

export function splitStock(entity_id: number, payload: StockPayload[]) {
  return api.post("/stocks/split", {
    entity_id,
    payload: JSON.stringify(payload),
  })
}

export function transformETBE(entity_id: number, payload: TransformETBEPayload[]) {
  return api.post("/stocks/transform", {
    entity_id, payload: JSON.stringify(payload)
  })
}