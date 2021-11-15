import { api, Api } from "common-v2/services/api"
import { Option } from "common-v2/utils/normalize"
import { LotQuery } from './hooks/lot-query'
import { StockQuery } from './hooks/stock-query'
import { LotList, Snapshot, Filter } from "./types"

const QUERY_RESET: Partial<LotQuery> = {
  limit: undefined,
  from_idx: undefined,
  order_by: undefined,
  direction: undefined,
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

export function downloadLots(query: LotQuery, selection: number[]) {
  return null
}

export function getLotFilters(field: Filter, query: LotQuery) {
  const params = { field, ...query, ...QUERY_RESET }
  return api.get<Api<Option[]>>("/lots/filters", { params }).then((res) => {
    const filters = res.data.data ?? []
    return filters.sort((a, b) => a.label.localeCompare(b.label, "fr"))
  })
}


export function sendLots(query: LotQuery, selection: number[]) {
  return api.post<Api<void>>(
    "/lots/send",
    selection.length === 0 ? query : { entity_id: query.entity_id, selection }
  )
}


// ENDPOINTS FOR STOCKS

export function getStocks(query: any) {
  return api.get<Api<any>>("/stocks", { params: query })
}

export function getStockFilters(field: Filter, query: LotQuery) {
  const params = { field, ...query, ...QUERY_RESET }
  return api.get<Api<Option[]>>("/stocks/filters", { params }).then((res) => {
    const filters = res.data.data ?? []
    return filters.sort((a, b) => a.label.localeCompare(b.label, "fr"))
  })
}
