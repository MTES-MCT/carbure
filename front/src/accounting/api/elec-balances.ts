import { api } from "common/services/api-fetch"
import { QueryParams } from "common/services/api-fetch.types"

export const getElecBalances = (
  query: QueryParams<"/tiruert/elec-operations/balance/">
) => {
  return api.GET("/tiruert/elec-operations/balance/", {
    params: {
      query,
    },
  })
}
