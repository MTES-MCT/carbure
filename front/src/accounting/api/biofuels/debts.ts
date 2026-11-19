import { api } from "common/services/api-fetch"
import { apiTypes } from "common/services/api-fetch.types"

export const getDebts = (entityId: number) => {
  return api.GET("/tiruert/operations/debts/", {
    params: { query: { entity_id: entityId } },
  })
}

export const simulateDebtRepayment = (
  entityId: number,
  data: apiTypes["DebtRepaymentSimulationInputRequest"]
) =>
  api.POST("/tiruert/operations/simulate_debt_repayment/", {
    params: { query: { entity_id: entityId } },
    body: data,
  })
