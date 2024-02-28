import { Api, api, download } from "common/services/api"
import { Option } from "common/utils/normalize"
import { lotFormToPayload, LotFormValue } from "lot-add/components/lot-form"
import { selectionOrQuery } from "transactions/api"
import {
  Filter,
  LotList,
  LotQuery,
  StockList,
  StockQuery,
  StockSummary
} from "transactions/types"
import { LotsDeleteResponse, LotSummary, LotsUpdateResponse, Snapshot } from "../types"

const QUERY_RESET: Partial<LotQuery> = {
  limit: undefined,
  from_idx: undefined,
  order_by: undefined,
  direction: undefined,
}

export function getYears(entity_id: number) {
  return api.get<Api<number[]>>("/transactions/admin/years", { params: { entity_id } })
}

export function getSnapshot(entity_id: number, year: number) {
  return api.get<Api<Snapshot>>("/transactions/admin/snapshot", {
    params: { entity_id, year },
  })
}

export function getLots(query: LotQuery) {
  return api.get<Api<LotList>>("/transactions/admin/lots", { params: query })
}

export function getStocks(query: StockQuery) {
  return api.get<Api<StockList>>("/transactions/admin/stocks", { params: query })
}

export function downloadLots(query: LotQuery, selection: number[]) {
  return download("/transactions/admin/lots", {
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
  return api.get<Api<LotSummary>>("/transactions/admin/lots/summary", {
    params: { ...query, selection, ...QUERY_RESET, short },
  })
}

export function getStocksSummary(
  query: StockQuery,
  selection: number[],
  short?: boolean
) {
  return api.get<Api<StockSummary>>("/transactions/admin/stocks/summary", {
    params: { ...query, selection, ...QUERY_RESET, short },
  })
}

export function getLotFilters(field: Filter, query: LotQuery) {
  const params = { field, ...query, ...QUERY_RESET }
  return api
    .get<Api<string[]>>("/transactions/admin/lots/filters", { params })
    .then((res) => res.data.data ?? [])
}

export function getStockFilters(field: Filter, query: StockQuery) {
  const params = { field, ...query, ...QUERY_RESET }
  return api
    .get<Api<Option[]>>("/transactions/admin/stocks/filters", { params })
    .then((res) => res.data.data ?? [])
}

export function pinLots(
  entity_id: number,
  selection: number[],
  notify_admin?: boolean,
  notify_auditor?: boolean
) {
  return api.post("/transactions/admin/lots/pin", {
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

  return api.post<Api<void>>("/transactions/admin/lots/comment", {
    entity_id: query.entity_id,
    selection,
    is_visible_by_admin,
    is_visible_by_auditor,
    comment,
  })
}

export function updateLots(
  entity_id: number,
  lots_ids: number[],
  updated_values: Partial<LotFormValue>,
  comment: string,
  dry_run?: boolean
) {
  return api.post<Api<LotsUpdateResponse>>("/transactions/admin/lots/update-many", {
    entity_id,
    lots_ids,
    comment,
    dry_run,
    ...lotFormToPayload(updated_values),
  })
}

export function deleteLots(
  entity_id: number,
  lots_ids: number[],
  comment: string,
  dry_run?: boolean
) {
  return api.post<Api<LotsDeleteResponse>>("/transactions/admin/lots/delete-many", {
    entity_id,
    lots_ids,
    comment,
    dry_run
  })
}
