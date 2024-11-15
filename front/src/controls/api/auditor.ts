import { Api, api, download } from "common/services/api"
import { api as apiFetch } from "common/services/api-fetch"
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
  console.log("OKOKOK 84")
  return apiFetch.GET("/v2/transactions/years", {
    params: {
      query: { entity_id },
    },
  })
}

export function getSnapshot(entity_id: number, year: number) {
  console.log("OKOKOK 85")
  return apiFetch.GET("/v2/transactions/snapshot", {
    params: {
      query: {  entity_id, year },
    },
  })
}

export function getLots(query: LotQuery) {
  console.log("OKOKOK 86")
  return apiFetch.GET("/v2/transactions/lots/", {
    params: {
      query:  query ,
    },
  })
}

export function getStocks(query: StockQuery) {
  console.log("OKOKOK 87")
  return apiFetch.GET("/v2/transactions/stocks/", {
    params: {
      query:  query ,
    },
  })
}

export function downloadLots(query: LotQuery, selection: number[]) {
  console.log("VERYUNSURE 88")
  return download("/transactions/audit/lots", {
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
  console.log("OKOKOK 89")
   return apiFetch.GET("/v2/transactions/lots/summary/", {
      params: { query: { ...query, selection, ...QUERY_RESET, short } },
    })
}

export function getStocksSummary(
  query: StockQuery,
  selection: number[],
  short?: boolean
) {
  console.log("OKOKOK 90")
  return apiFetch.GET("/v2/transactions/stocks/summary/", {
      params: { query: { ...query, selection, ...QUERY_RESET, short } },
    })
}

export async function getLotFilters(field: Filter, query: LotQuery) {
  console.log("OKOKOK 91")
  
   const res = await apiFetch.GET("/v2/transactions/lots/filters/", {
        params: { query: { field, ...query, ...QUERY_RESET } },
      })
      return res.data ?? []
}

export async function getStockFilters(field: Filter, query: StockQuery) {
  console.log("OKOKOK 92")
  const res = await apiFetch.GET("/v2/transactions/stocks/filters/", {
    params: { query: { field, ...query, ...QUERY_RESET } },
  })
  return res.data ?? []
}

export function pinLots(
  entity_id: number,
  selection: number[],
  notify_admin?: boolean,
  notify_auditor?: boolean
) {
  console.log("OKOKOK 93")
  return apiFetch.POST("/v2/transactions/lots/toggle-pin/", {
    params: { query:  {entity_id}  },
    body: {
      selection,
      notify_admin,
      notify_auditor,
    },
  })
}

export async function commentLots(
  query: LotQuery,
  selection: number[] | undefined,
  comment: string,
  is_visible_by_admin?: boolean,
  is_visible_by_auditor?: boolean
) {
  console.log("OKOKOK 94")
  if (!comment) return

  return apiFetch.POST("/v2/transactions/lots/add-comment/", {
    params: { query:  query  },
    body: {
      entity_id: query.entity_id,
      selection,
      is_visible_by_admin,
      is_visible_by_auditor,
      comment,
    },
  })
}

export async function markAsConform(entity_id: number, selection: number[]) {
  console.log("VERYUNSURE 95")
  return api.post<Api<void>>("/transactions/audit/lots/mark-as-conform", {
    entity_id,
    selection,
  })
}

export async function markAsNonConform(entity_id: number, selection: number[]) {
  console.log("VERYUNSURE 96")
  return api.post<Api<void>>("/transactions/audit/lots/mark-as-nonconform", {
    entity_id,
    selection,
  })
}
