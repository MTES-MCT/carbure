import { Api, api, download } from "common/services/api"
import { api as apiFetch } from "common/services/api-fetch"
import { Option } from "common/utils/normalize"
import { lotFormToPayload, LotFormValue } from "lot-add/components/lot-form"
import { selectionOrQuery } from "transactions/api"
import {
  Filter,
  LotList,
  LotQuery,
  StockList,
  StockQuery,
  StockSummary,
} from "transactions/types"
import {
  LotsDeleteResponse,
  LotSummary,
  LotsUpdateResponse,
  Snapshot,
} from "../types"

const QUERY_RESET: Partial<LotQuery> = {
  limit: undefined,
  from_idx: undefined,
  order_by: undefined,
  direction: undefined,
}

export function getYears(entity_id: number) {
  console.log("OKOKOK 71")
  // return api.get<Api<number[]>>("/transactions/admin/years", {
  //   params: { entity_id },
  // })
  return apiFetch.GET("/v2/transactions/years", {
    params: {
      query: { entity_id },
    },
  })
}

export function getSnapshot(entity_id: number, year: number) {
  console.log("OKOKOK 72")
  // return api.get<Api<Snapshot>>("/v2/transactions/snapshot", {
  //   params: { entity_id, year },
  // })
  return apiFetch.GET("/v2/transactions/snapshot", {
    params: {
      query: {  entity_id, year },
    },
  })
}

export function getLots(query: LotQuery) {
  console.log("OKOKOK 73")
  // return api.get<Api<LotList>>("/transactions/admin/lots", { params: query })
  return apiFetch.GET("/v2/transactions/lots/", {
    params: {
      query:  query ,
    },
  })
}

export function getStocks(query: StockQuery) {
  console.log("OKOKOK 74")
  // return api.get<Api<StockList>>("/transactions/admin/stocks", {
  //   params: query,
  // })

  return apiFetch.GET("/v2/transactions/stocks/", {
    params: {
      query:  query ,
    },
  })
}

export function downloadLots(query: LotQuery, selection: number[]) {
  console.log("VERYUNSURE 75")
  return download("/v2/transactions/lots/export/", {
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
  console.log("OKOKOK 76")
  // return api.get<Api<LotSummary>>("/transactions/admin/lots/summary", {
  //   params: { ...query, selection, ...QUERY_RESET, short },
  // })

  return apiFetch.GET("/v2/transactions/lots/summary/", {
    params: { query: { ...query, selection, ...QUERY_RESET, short } },
  })
}

export function getStocksSummary(
  query: StockQuery,
  selection: number[],
  short?: boolean
) {
  console.log("OKOKOK 77")
  // return api.get<Api<StockSummary>>("/transactions/admin/stocks/summary", {
  //   params: { ...query, selection, ...QUERY_RESET, short },
  // })

  return apiFetch.GET("/v2/transactions/stocks/summary/", {
    params: { query: { ...query, selection, ...QUERY_RESET, short } },
  })
}

export async function getLotFilters(field: Filter, query: LotQuery) {
  console.log("OKOKOK 78")
  // const params = { field, ...query, ...QUERY_RESET }
  // return api
  //   .get<Api<string[]>>("/v2/transactions/lots/filters", { params })
  //   .then((res) => res.data ?? [])
  
    const res = await apiFetch.GET("/v2/transactions/lots/filters/", {
      params: { query: { field, ...query, ...QUERY_RESET } },
    })
    return res.data ?? []
}

export async function getStockFilters(field: Filter, query: StockQuery) {
  console.log("OKOKOK 79")
  // const params = { field, ...query, ...QUERY_RESET }
  // return api
  //   .get<Api<Option[]>>("/transactions/admin/stocks/filters", { params })
  //   .then((res) => res.data.data ?? [])
  
  
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
  console.log("VERYUNSURE 80")
  // return api.post("/transactions/admin/lots/pin", {
  //   entity_id,
  //   selection,
  //   notify_admin,
  //   notify_auditor,
  // })

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
  console.log("OKOKOK 81")
  if (!comment) return

  // return api.post<Api<void>>("/v2/transactions/lots/add-comment/", {
  //   entity_id: query.entity_id,
  //   selection,
  //   is_visible_by_admin,
  //   is_visible_by_auditor,
  //   comment,
  // })

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

export function updateLots(
  entity_id: number,
  lots_ids: number[],
  updated_values: Partial<LotFormValue>,
  comment: string,
  dry_run?: boolean
) {
  console.log("VERYUNSURE 82")
  return api.post<Api<LotsUpdateResponse>>(
    "/transactions/admin/lots/update-many",
    {
      entity_id,
      lots_ids,
      comment,
      dry_run,
      ...lotFormToPayload(updated_values),
    }
  )
}

export function deleteLots(
  entity_id: number,
  lots_ids: number[],
  comment: string,
  dry_run?: boolean
) {
  console.log("VERYUNSURE 83")
  return api.post<Api<LotsDeleteResponse>>(
    "/transactions/admin/lots/delete-many",
    {
      entity_id,
      lots_ids,
      comment,
      dry_run,
    }
  )
}
