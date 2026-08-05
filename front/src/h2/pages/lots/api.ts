import { api } from "common/services/api-fetch"
import { ActionFilter, ActionQuery } from "h2/types"

export function getActionYears(entity_id: number) {
  return api
    .GET("/traceability/actions/filters/", {
      params: {
        query: {
          entity_id,
          filter: ActionFilter.working_year,
        },
      },
    })
    .then((res) => ({
      ...res,
      data: res.data?.map(Number) ?? [],
    }))
}

export function getActionFilters(filter: ActionFilter, query: ActionQuery) {
  return api
    .GET("/traceability/actions/filters/", {
      params: { query: { ...query, filter } },
    })
    .then((res) => res.data ?? [])
}

export function getActions(query: ActionQuery) {
  return api.GET("/traceability/actions/", { params: { query } })
}
