import { api } from "common/services/api-fetch"
import { BalancesFilter, BalancesQuery } from "./types"

export const getBalances = (query: BalancesQuery) => {
  return api.GET("/tiruert/operations/balance/", {
    params: {
      query,
    },
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
