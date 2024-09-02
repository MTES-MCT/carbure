import { CBQUERY_RESET } from "common/hooks/query-builder"
import api, { Api } from "common/services/api"
import { ChargePointsListData, ChargePointsListQuery } from "./types"

export function getChargePointsList(query: ChargePointsListQuery) {
  return api.get<Api<ChargePointsListData>>("elec/charge-points/list", {
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
    >("/elec/charge-points-filters", { params })
    .then((res) => res.data.data?.filter_values ?? [])
}
