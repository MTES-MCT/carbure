import { api } from "common/services/api-fetch"
import { Balance, BalancesFilter, BalancesQuery } from "./types"

export const getBalances = (query: BalancesQuery) => {
  return api
    .GET("/tiruert/operations/balance/", {
      params: {
        query,
      },
    })
    .then((response) => {
      const results = response.data?.results
      return {
        ...response,
        data: {
          ...response.data,
          results: results as Balance[],
        },
      }
    })
}

export const getBalanceFilters = (
  query: BalancesQuery,
  filter: BalancesFilter
) => {
  return api.GET("/tiruert/operations/balance/filters/", {
    params: { query: { ...query, filter } },
  })
}
