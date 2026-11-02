import { api } from "common/services/api-fetch"

export const getDebts = (entityId: number) => {
  return api.GET("/tiruert/operations/debts/", {
    params: { query: { entity_id: entityId } },
  })
}
