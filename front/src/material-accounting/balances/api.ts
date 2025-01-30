import { api } from "common/services/api-fetch"
import { BalancesQuery } from "./types"

export const getBalances = (query: BalancesQuery) => {
  return api.GET("/tiruert/operations/balance/", {
    params: {
      query,
    },
  })
}
