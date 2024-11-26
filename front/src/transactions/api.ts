import { Entity } from "carbure/types"
import { api, Api, download } from "common/services/api"
import { api as apiFetch } from "common/services/api-fetch"
import { Option } from "common/utils/normalize"
import {
  LotList,
  LotQuery,
  StockQuery,
  Filter,
  StockList,
  LotSummary,
  DeclarationSummary,
  StockSummary,
  StockPayload,
  TransformETBEPayload,
} from "./types"

const QUERY_RESET: Partial<LotQuery> = {
  limit: undefined,
  from_idx: undefined,
  order_by: undefined,
  direction: undefined,
}

// BUG
export function getYears(entity_id: number) {
  return apiFetch
    .GET("/transactions/years", {
      params: {
        query: {
          entity_id,
        },
      },
    })

    .then((res) => ({
      ...res,
      // @ts-ignore temporary fix
      data: res?.data ? (res?.data as number[]) : [],
    }))
}

export function getSnapshot(entity_id: number, year: number) {
  return apiFetch.GET("/transactions/snapshot", {
    params: { query: { entity_id, year } },
  })
}

// ENDPOINTS FOR LOTS
// BUG
export function getLots(query: LotQuery) {
  return api.get<Api<LotList>>("/transactions/lots", { params: query })
}

// BUG
export function importLots(entity_id: number, file: File) {
  return api.post<Api<void>>("/transactions/lots/add-excel", {
    entity_id,
    file,
  })
}

// BUG
export function downloadLots(query: LotQuery, selection: number[]) {
  return download("/transactions/lots", {
    ...selectionOrQuery(
      { ...query, limit: undefined, from_idx: undefined },
      selection
    ),
    export: true,
  })
}

// BUG
export function getLotsSummary(
  query: LotQuery,
  selection: number[],
  short?: boolean
) {
  return api.get<Api<LotSummary>>("/transactions/lots/summary", {
    params: { ...query, selection, ...QUERY_RESET, short },
  })
}

// BUG
export function getDeclarations(entity_id: number, year: number) {
  return api.get<Api<DeclarationSummary[]>>("/transactions/declarations", {
    params: { entity_id, year },
  })
}

// Fonctionne mais pas testé dans des conditions réelles
export function validateDeclaration(entity_id: number, period: number) {
  return apiFetch.POST("/transactions/lots/declarations-validate/", {
    params: { query: { entity_id } },
    body: { period },
  })
}

// Non testé
export function invalidateDeclaration(entity_id: number, period: number) {
  return apiFetch.POST("/transactions/lots/declarations-invalidate/", {
    params: { query: { entity_id } },
    body: { period },
  })
}

// BUG
export function getLotFilters(field: Filter, query: LotQuery) {
  const params = { field, ...query, ...QUERY_RESET }
  return api
    .get<Api<string[]>>("/transactions/lots/filters", { params })
    .then((res) => {
      // @ts-ignore temporary fix
      return res.data ? (res.data as string[]) : []
    })
}

// endpoint non trouvé
export function duplicateLots(entity_id: number, lot_id: number) {
  return api.post<Api<void>>("/transactions/lots/duplicate", {
    entity_id,
    lot_id,
  })
}

// BUG
export function sendLots(query: LotQuery, selection?: number[]) {
  return api.post<Api<void>>(
    "/transactions/lots/send",
    selectionOrQuery(query, selection)
  )
}

// BUG
export function acceptReleaseForConsumption(
  query: LotQuery,
  selection?: number[]
) {
  return api.post<Api<void>>(
    "/transactions/lots/accept-release-for-consumption",
    selectionOrQuery(query, selection)
  )
}

// BUG
export function acceptInStock(query: LotQuery, selection?: number[]) {
  return api.post<Api<void>>(
    "/transactions/lots/accept-in-stock",
    selectionOrQuery(query, selection)
  )
}

// BUG
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

  return api.post<Api<void>>("/transactions/lots/accept-trading", {
    ...selectionOrQuery(query, selection),
    ...params,
    certificate,
  })
}

// BUG
export function acceptForProcessing(
  query: LotQuery,
  selection: number[] | undefined,
  processing_entity_id: number
) {
  return api.post<Api<void>>("/transactions/lots/accept-processing", {
    ...selectionOrQuery(query, selection),
    processing_entity_id,
  })
}

// BUG
export function acceptForBlending(
  query: LotQuery,
  selection: number[] | undefined
) {
  return api.post<Api<void>>(
    "/transactions/lots/accept-blending",
    selectionOrQuery(query, selection)
  )
}

//BUG
export function acceptForConsumption(
  query: LotQuery,
  selection: number[] | undefined
) {
  return api.post<Api<void>>(
    "/transactions/lots/accept-consumption",
    selectionOrQuery(query, selection)
  )
}

// BUG
export function acceptForDirectDelivery(
  query: LotQuery,
  selection: number[] | undefined
) {
  return api.post<Api<void>>(
    "/transactions/lots/accept-direct-delivery",
    selectionOrQuery(query, selection)
  )
}

// BUG
export function acceptForExport(
  query: LotQuery,
  selection: number[] | undefined
) {
  return api.post<Api<void>>(
    "/transactions/lots/accept-export",
    selectionOrQuery(query, selection)
  )
}

// BUG
export function deleteLots(query: LotQuery, selection?: number[]) {
  return api.post<Api<void>>(
    "/transactions/lots/delete",
    selectionOrQuery(query, selection)
  )
}

// BUG
export function rejectLots(query: LotQuery, selection?: number[]) {
  return api.post<Api<void>>(
    "/transactions/lots/reject",
    selectionOrQuery(query, selection)
  )
}

// OK
export function requestFix(entity_id: number, lot_ids: number[]) {
  return apiFetch.POST("/transactions/lots/request-fix/", {
    params: { query: { entity_id } },
    body: { lot_ids },
  })
}

// OK
export function markAsFixed(entity_id: number, lot_ids: number[]) {
  return apiFetch.POST("/transactions/lots/submit-fix/", {
    params: { query: { entity_id } },
    body: { lot_ids },
  })
}

// OK
export function approveFix(entity_id: number, lot_ids: number[]) {
  return apiFetch.POST("/transactions/lots/approuve-fix/", {
    params: { query: { entity_id } },
    body: { lot_ids },
  })
}

// Meme code que requestFix
export function recallLots(entity_id: number, lot_ids: number[]) {
  return apiFetch.POST("/transactions/lots/request-fix/", {
    params: { query: { entity_id } },
    body: { lot_ids },
  })
}

// BUG
export async function commentLots(
  query: LotQuery,
  selection: number[] | undefined,
  comment: string
) {
  if (!comment) return

  return api.post<Api<void>>("/transactions/lots/comment", {
    ...selectionOrQuery(query, selection),
    comment,
  })
}

export function selectionOrQuery(query: LotQuery, selection?: number[]) {
  if (!selection || selection.length === 0) return query
  else return { entity_id: query.entity_id, selection }
}

// ENDPOINTS FOR STOCKS

// BUG
export function getStocks(query: StockQuery) {
  return api.get<Api<StockList>>("/transactions/stocks", { params: query })
}

// BUG
export function downloadStocks(query: StockQuery, selection: number[]) {
  return download("/transactions/stocks", {
    ...selectionOrQuery(
      { ...query, from_idx: undefined, limit: undefined },
      selection
    ),
    export: true,
  })
}

// BUG
export function getStockSummary(
  query: StockQuery,
  selection: number[],
  short?: boolean
) {
  return api.get<Api<StockSummary>>("/transactions/stocks/summary", {
    params: { ...query, selection, ...QUERY_RESET, short },
  })
}

// BUG
export function getStockFilters(field: Filter, query: StockQuery) {
  const params = { field, ...query, ...QUERY_RESET }
  return api
    .get<Api<Option[]>>("/transactions/stocks/filters", { params })
    .then((res) => res.data.data ?? [])
}

// BUG
export function splitStock(entity_id: number, payload: StockPayload[]) {
  return api.post("/transactions/stocks/split", {
    entity_id,
    payload: JSON.stringify(payload),
  })
}

// Non testé
export function transformETBE(
  entity_id: number,
  payload: TransformETBEPayload[]
) {
  return apiFetch.POST("/transactions/stocks/transform/", {
    params: { query: { entity_id } },
    body: { payload: JSON.stringify(payload) },
  })
}

// Non testé
export function cancelTransformations(entity_id: number, stock_ids: number[]) {
  return apiFetch.POST("/transactions/stocks/cancel-transformation/", {
    params: { query: { entity_id } },
    body: { stock_ids },
  })
}

// Non testé
export function flushStocks(
  entity_id: number,
  stock_ids: number[],
  free_field: string
) {
  return apiFetch.POST("/transactions/stocks/flush/", {
    params: { query: { entity_id } },
    body: { stock_ids, free_field },
  })
}

// export function cancelAcceptLots(entity_id: number, lot_ids: number[]) {
//   return api.post("/transactions/lots/cancel-accept", { entity_id, lot_ids })
// }
export function cancelAcceptLots(entity_id: number, lot_ids: number[]) {
  return apiFetch.POST("/transactions/lots/cancel-accept/", {
    params: { query: { entity_id } },
    body: { lot_ids },
  })
}
