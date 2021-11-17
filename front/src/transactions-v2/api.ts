import { api, Api } from "common-v2/services/api"
import { Option } from "common-v2/utils/normalize"
import { LotQuery } from "./hooks/lot-query"
import { StockQuery } from "./hooks/stock-query"
import { LotList, Snapshot, Filter, StockList } from "./types"

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
  // prettier-ignore
  const params = selection.length > 0
    ? { entity_id: query.entity_id, selection }
    : query

  return api.post<Api<void>>("/lots/send", params)
}

// ENDPOINTS FOR STOCKS

export function getStocks(query: StockQuery) {
  return api.get<Api<StockList>>("/stocks", { params: query })
}

export function getStockFilters(field: Filter, query: LotQuery) {
  const params = { field, ...query, ...QUERY_RESET }
  return api.get<Api<Option[]>>("/stocks/filters", { params }).then((res) => {
    const filters = res.data.data ?? []
    return filters.sort((a, b) => a.label.localeCompare(b.label, "fr"))
  })
}
