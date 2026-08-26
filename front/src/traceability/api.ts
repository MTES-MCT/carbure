import { api } from "common/services/api-fetch"
import { ActionFilter, ActionIndustry, ActionQuery } from "traceability/types"

export function getActionYears(
  entity_id: number,
  industry: ActionIndustry,
  query: Partial<ActionQuery>
) {
  return api.GET("/traceability/actions/years/", {
    params: {
      query: {
        ...query,
        entity_id,
        industry,
      },
    },
  })
}

export function getActionFilters(
  filter: ActionFilter,
  industry: ActionIndustry,
  query: ActionQuery
) {
  return api
    .GET("/traceability/actions/filters/", {
      params: {
        query: { ...query, filter, industry },
      },
    })
    .then((res) => res.data ?? [])
}

export function getActions(industry: ActionIndustry, query: ActionQuery) {
  return api.GET("/traceability/actions/", {
    params: { query: { ...query, industry } },
  })
}

export function getActionDetail(
  entity_id: number,
  id: number,
  industry: ActionIndustry
) {
  return api.GET("/traceability/actions/{id}/", {
    params: {
      path: { id },
      query: { entity_id, industry },
    },
  })
}
