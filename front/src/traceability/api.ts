import { api } from "common/services/api-fetch"
import { ActionFilter, ActionQuery } from "traceability/types"

export function getActionYears(entity_id: number, query: Partial<ActionQuery>) {
  return api.GET("/traceability/actions/years/", {
    params: {
      query: {
        ...query,
        entity_id,
      },
    },
  })
}

export function getActionFilters(filter: ActionFilter, query: ActionQuery) {
  return api
    .GET("/traceability/actions/filters/", {
      params: {
        query: { ...query, filter },
      },
    })
    .then((res) => res.data ?? [])
}

export function getActions(query: ActionQuery) {
  return api.GET("/traceability/actions/", {
    params: { query },
  })
}
