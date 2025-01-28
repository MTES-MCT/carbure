import { OperationsFilter, OperationsQuery } from "./types"
import { api as apiFetch } from "common/services/api-fetch"
export const getOperationsFilters = (
  filter: string,
  query: OperationsQuery
) => {
  return apiFetch.GET("/tiruert/operations/filters/", {
    params: {
      query: {
        ...query,
        entity_id: `${query.entity_id}`,
        status: query.statuses,
        filter: filter as OperationsFilter,
      },
    },
  })
}
