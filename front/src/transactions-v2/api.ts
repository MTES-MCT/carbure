import { api, Api } from "common-v2/api"
import { Option } from "common-v2/hooks/normalize"
import { LotList, Snapshot, Filter, LotQuery } from "./types"

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

export function getLots(query: LotQuery) {
  return api.get<Api<LotList>>("/lots", { params: query })
}

export function downloadLots(query: LotQuery, selection: number[]) {
  return
}

export function getFilters(field: Filter, query: LotQuery) {
  return api.get<Api<Option[]>>("/filters", {
    params: { field, ...query, ...QUERY_RESET },
  })
}

export function sendLots(query: LotQuery, selection: number[]) {
  return api.post<Api<void>>(
    "/lots/send",
    selection.length === 0 ? query : { entity_id: query.entity_id, selection }
  )
}
