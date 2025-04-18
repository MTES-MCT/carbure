import { Balance, BalancesFilter, BalancesQuery } from "accounting/types"
import { api } from "common/services/api-fetch"
import { apiTypes, QueryParams } from "common/services/api-fetch.types"

/** Balances */
export const getBalanceFilters = (
  query: BalancesQuery,
  filter: BalancesFilter
) => {
  return api.GET("/tiruert/operations/balance/filters/", {
    params: { query: { ...query, filter } },
  })
}

export const getBalances = <
  BalanceType extends
    | Balance
    | apiTypes["BalanceBySector"]
    | apiTypes["BalanceByDepot"] = Balance,
>(
  query: QueryParams<"/tiruert/operations/balance/">
) => {
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
          results: results as BalanceType[],
        },
      }
    })
}
