import { api } from "common/services/api-fetch"
import { ActionFilter, ActionFixedQuery, ActionQuery } from "traceability/types"

const convertFixedQueryToPayload = ({
  industry,
  ...rest
}: ActionFixedQuery) => {
  return {
    ...rest,
    industry: [industry],
  }
}
export function getActionYears(
  entity_id: number,
  fixedQuery: ActionFixedQuery
) {
  return api
    .GET("/traceability/actions/filters/", {
      params: {
        query: {
          entity_id,
          filter: ActionFilter.working_year,
          ...convertFixedQueryToPayload(fixedQuery),
        },
      },
    })
    .then((res) => ({
      ...res,
      data: res.data?.map(Number) ?? [],
    }))
}

export function getActionFilters(
  filter: ActionFilter,
  query: ActionQuery,
  fixedQuery: ActionFixedQuery
) {
  return api
    .GET("/traceability/actions/filters/", {
      params: {
        query: {
          ...query,
          ...convertFixedQueryToPayload(fixedQuery),
          filter,
        },
      },
    })
    .then((res) => res.data ?? [])
}

export function getActions(query: ActionQuery, fixedQuery: ActionFixedQuery) {
  return api.GET("/traceability/actions/", {
    params: { query: { ...query, ...convertFixedQueryToPayload(fixedQuery) } },
  })
}
