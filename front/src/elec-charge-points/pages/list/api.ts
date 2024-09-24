import { CBQUERY_RESET } from "common/hooks/query-builder"
import api, { Api, download } from "common/services/api"
import { selectionOrQuery } from "common/utils/pagination"
import { ChargePointsListData, ChargePointsListQuery } from "./types"

export function getChargePointsList(query: ChargePointsListQuery) {
  const { year, ...params } = query
  return api.get<Api<ChargePointsListData>>("elec/cpo/charge-points", {
    params,
  })
}

export function getChargePointsFilters(
  field: string,
  query: ChargePointsListQuery
) {
  const { year, ...params } = { filter: field, ...query, ...CBQUERY_RESET }

  return api
    .get<
      Api<{ filter_values: (string | boolean)[] }>
    >("/elec/cpo/charge-points/filters", { params })
    .then((res) => res.data.data?.filter_values ?? [])
}

export function downloadChargePointsList(
  { year, ...params }: ChargePointsListQuery,
  selection: number[]
) {
  return download("/elec/cpo/charge-points", {
    ...selectionOrQuery(
      { ...params, from_idx: undefined, limit: undefined },
      selection
    ),
    export: true,
  })
}
