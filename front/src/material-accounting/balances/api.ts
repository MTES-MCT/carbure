import { api } from "common/services/api-fetch"

export const getBalances = (entity_id: number) => {
  return api.GET("/tiruert/operations/balance/", {
    params: {
      query: {
        entity_id,
      },
    },
  })
}
