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
        status: query.statuses,
        filter: filter as OperationsFilter,
      },
    },
  })
}

export const getOperations = (query: OperationsQuery) => {
  return apiFetch.GET("/tiruert/operations/", {
    params: {
      query: {
        ...query,
        status: query.statuses,
      },
    },
  })
}
