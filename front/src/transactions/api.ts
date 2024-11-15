import { EntityPreview } from "carbure/types"
import { api, Api, download } from "common/services/api"
import { api as apiFetch } from "common/services/api-fetch"
import { Option } from "common/utils/normalize"
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
  TransformETBEPayload,
} from "./types"

const QUERY_RESET: Partial<LotQuery> = {
  limit: undefined,
  from_idx: undefined,
  order_by: undefined,
  direction: undefined,
}

export function getYears(entity_id: number) {
  console.log("OKOKOK 16")
  return apiFetch.GET("/v2/transactions/years", {
    params: {
      query: { entity_id },
    },
  })
}

export function getSnapshot(entity_id: number, year: number) {
  console.log("OKOKOK 17")
  return apiFetch.GET("/v2/transactions/snapshot", {
    params: {
      query: {  entity_id, year },
    },
  })
}

// ENDPOINTS FOR LOTS

export function getLots(query: LotQuery) {
  console.log("OKOKOK 18")
  return apiFetch.GET("/v2/transactions/lots/", {
    params: {
      query:  query ,
    },
  })
}

export function importLots(entity_id: number, file: File) {
  console.log("VERYUNSURE 19")
  return api.post<Api<void>>("/transactions/lots/add-excel", {
    entity_id,
    file,
  })
}

export function downloadLots(query: LotQuery, selection: number[]) {
  console.log("VERYUNSURE 20")
  return download("/transactions/lots", {
    ...selectionOrQuery(
      { ...query, limit: undefined, from_idx: undefined },
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
  console.log("OKOKOK 21")
 return apiFetch.GET("/v2/transactions/lots/summary/", {
       params: { query: { ...query, selection, ...QUERY_RESET, short } },
     })
}

export function getDeclarations(entity_id: number, year: number) {
  console.log("OKOKOK 22")
  // return api.get<Api<DeclarationSummary[]>>("/transactions/declarations", {
  //   params: { entity_id, year },
  // })

  return apiFetch.GET("/v2/transactions/lots/declarations/", {
    params: { query: { entity_id, year } },
  })
}

export function validateDeclaration(entity_id: number, period: number) {
  console.log("VERYUNSURE 23")
  return api.post<Api<void>>("/transactions/declarations/validate", {
    entity_id,
    period,
  })
}

export function invalidateDeclaration(entity_id: number, period: number) {
  console.log("VERYUNSURE 24")
  return api.post<Api<void>>("/transactions/declarations/invalidate", {
    entity_id,
    period,
  })
}

export async function getLotFilters(field: Filter, query: LotQuery) {
  console.log("OKOKOK 25")
  const params = { field, ...query, ...QUERY_RESET }
    const res = await apiFetch.GET("/v2/transactions/lots/filters/", {
      params: { query: { field, ...query, ...QUERY_RESET } },
    })
    return res.data ?? []
}

export function duplicateLots(entity_id: number, lot_id: number) {
  console.log("VERYUNSURE 26")
  return api.post<Api<void>>("/transactions/lots/duplicate", {
    entity_id,
    lot_id,
  })
}

export function sendLots(query: LotQuery, selection?: number[]) {
  console.log("VERYUNSURE 27")
  return api.post<Api<void>>(
    "/transactions/lots/send",
    selectionOrQuery(query, selection)
  )
}

export function acceptReleaseForConsumption(
  query: LotQuery,
  selection?: number[]
) {
  console.log("VERYUNSURE 28")
  return api.post<Api<void>>(
    "/transactions/lots/accept-release-for-consumption",
    selectionOrQuery(query, selection)
  )
}

export function acceptInStock(query: LotQuery, selection?: number[]) {
  console.log("VERYUNSURE 29")
  return api.post<Api<void>>(
    "/transactions/lots/accept-in-stock",
    selectionOrQuery(query, selection)
  )
}


export function acceptForTrading(
  query: LotQuery,
  selection: number[] | undefined,
  client: EntityPreview | string,
  certificate: string
) {
  console.log("VERYUNSURE 30")
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


export function acceptForProcessing(
  query: LotQuery,
  selection: number[] | undefined,
  processing_entity_id: number
) {
  console.log("VERYUNSURE 31")
  return api.post<Api<void>>("/transactions/lots/accept-processing", {
    ...selectionOrQuery(query, selection),
    processing_entity_id,
  })
}


export function acceptForBlending(
  query: LotQuery,
  selection: number[] | undefined
) {
  console.log("VERYUNSURE 32")
  return api.post<Api<void>>(
    "/transactions/lots/accept-blending",
    selectionOrQuery(query, selection)
  )
}

export function acceptForConsumption(
  query: LotQuery,
  selection: number[] | undefined
) {
  console.log("VERYUNSURE 33")
  return api.post<Api<void>>(
    "/transactions/lots/accept-consumption",
    selectionOrQuery(query, selection)
  )
}

export function acceptForDirectDelivery(
  query: LotQuery,
  selection: number[] | undefined
) {
  console.log("VERYUNSURE 34")
  return api.post<Api<void>>(
    "/transactions/lots/accept-direct-delivery",
    selectionOrQuery(query, selection)
  )
}

export function acceptForExport(
  query: LotQuery,
  selection: number[] | undefined
) {
  console.log("VERYUNSURE 35")
  return api.post<Api<void>>(
    "/transactions/lots/accept-export",
    selectionOrQuery(query, selection)
  )
}

export function deleteLots(query: LotQuery, selection?: number[]) {
  console.log("VERYUNSURE 36")
  return api.post<Api<void>>(
    "/transactions/lots/delete",
    selectionOrQuery(query, selection)
  )
}

export function rejectLots(query: LotQuery, selection?: number[]) {
  console.log("VERYUNSURE 37")
  return api.post<Api<void>>(
    "/transactions/lots/reject",
    selectionOrQuery(query, selection)
  )
}

export function requestFix(entity_id: number, lot_ids: number[]) {
  console.log("VERYUNSURE 38")
  return api.post<Api<void>>("/transactions/lots/request-fix", {
    entity_id,
    lot_ids,
  })
}

export function markAsFixed(entity_id: number, lot_ids: number[]) {
  console.log("VERYUNSURE 39")
  return api.post<Api<void>>("/transactions/lots/submit-fix", {
    entity_id,
    lot_ids,
  })
}

export function approveFix(entity_id: number, lot_ids: number[]) {
  console.log("VERYUNSURE 40")
  return api.post<Api<void>>("/transactions/lots/approve-fix", {
    entity_id,
    lot_ids,
  })
}

export function recallLots(entity_id: number, lot_ids: number[]) {
  console.log("VERYUNSURE 41")
  return api.post<Api<void>>("/transactions/lots/request-fix", {
    entity_id,
    lot_ids,
  })
}

export async function commentLots(
  query: LotQuery,
  selection: number[] | undefined,
  comment: string
) {
  if (!comment) return
  
  console.log("VERYUNSURE 42")
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

export function getStocks(query: StockQuery) {
  console.log("OKOKOK 43")
  return apiFetch.GET("/v2/transactions/stocks/", {
    params: {
      query:  query ,
    },
  })
}

export function downloadStocks(query: StockQuery, selection: number[]) {
  console.log("VERYUNSURE 44")
  return download("/transactions/stocks", {
    ...selectionOrQuery(
      { ...query, from_idx: undefined, limit: undefined },
      selection
    ),
    export: true,
  })
}

export function getStockSummary(
  query: StockQuery,
  selection: number[],
  short?: boolean
) {
  console.log("OKOKOK 45")
  return apiFetch.GET("/v2/transactions/stocks/summary/", {
      params: { query: { ...query, selection, ...QUERY_RESET, short } },
    })
}

export async function getStockFilters(field: Filter, query: StockQuery) {
  console.log("OKOKOK 46")
  const res = await apiFetch.GET("/v2/transactions/stocks/filters/", {
    params: { query: { field, ...query, ...QUERY_RESET } },
  })
  return res.data ?? []
}

export function splitStock(entity_id: number, payload: StockPayload[]) {
  console.log("VERYUNSURE 47")
  return api.post("/transactions/stocks/split", {
    entity_id,
    payload: JSON.stringify(payload),
  })
}

export function transformETBE(
  entity_id: number,
  payload: TransformETBEPayload[]
) {
  console.log("VERYUNSURE 48")
  return api.post("/transactions/stocks/transform", {
    entity_id,
    payload: JSON.stringify(payload),
  })
}

export function cancelTransformations(entity_id: number, stock_ids: number[]) {
  console.log("VERYUNSURE 49")
  return api.post("/transactions/stocks/cancel-transformation", {
    entity_id,
    stock_ids,
  })
}

export function flushStocks(
  entity_id: number,
  stock_ids: number[],
  free_field: string
) {
  console.log("VERYUNSURE 50")
  return api.post("/transactions/stocks/flush", {
    entity_id,
    stock_ids,
    free_field,
  })
}

export function cancelAcceptLots(entity_id: number, lot_ids: number[]) {
  console.log("VERYUNSURE 51")
  return api.post("/transactions/lots/cancel-accept", { entity_id, lot_ids })
}
