import { CBQUERY_RESET } from "common/hooks/query-builder"
import api, { Api, download } from "common/services/api"
import { ChargePointsListData, ChargePointsListQuery } from "./types"

export function getChargePointsList(query: ChargePointsListQuery) {
  return api.get<Api<ChargePointsListData>>("elec/cpo/charge-points", {
    params: query,
  })
}

export function getChargePointsFilters(
  field: string,
  query: ChargePointsListQuery
) {
  const params = { filter: field, ...query, ...CBQUERY_RESET }

  return api
    .get<
      Api<{ filter_values: string[] }>
    >("/elec/cpo/charge-points/filters", { params })
    .then((res) => res.data.data?.filter_values ?? [])
}

export function selectionOrQuery(
  query: Partial<ChargePointsListQuery>,
  selection?: number[]
) {
  if (!selection || selection.length === 0) return query
  else return { entity_id: query.entity_id, selection }
}

export function downloadChargePointsList(
  query: ChargePointsListQuery,
  selection: number[]
) {
  return download("/elec/cpo/charge-points", {
    ...selectionOrQuery(
      { ...query, from_idx: undefined, limit: undefined },
      selection
    ),
    export: true,
  })
}
