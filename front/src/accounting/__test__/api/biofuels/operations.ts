import { HttpResponse } from "msw"
import { http } from "common/__test__/http"
import { Operation } from "accounting/types"
import { operationCredit } from "accounting/__test__/data/biofuels/operation"

export const okSimulateMinMax = http.post(
  "/tiruert/operations/simulate/min_max/",
  () => {
    return HttpResponse.json({
      min_avoided_emissions: 10,
      max_avoided_emissions: 50,
    })
  }
)

export const okSimulateMinMaxWithEqualValues = http.post(
  "/tiruert/operations/simulate/min_max/",
  () => {
    return HttpResponse.json({
      min_avoided_emissions: 10,
      max_avoided_emissions: 10.65,
    })
  }
)

export const okSimulateMinMaxWithZeroValues = http.post(
  "/tiruert/operations/simulate/min_max/",
  () => {
    return HttpResponse.json({
      min_avoided_emissions: 0.1,
      max_avoided_emissions: 0.2,
    })
  }
)

export const okSimulateOperation = http.post(
  "/tiruert/operations/simulate/",
  () => {
    return HttpResponse.json({
      selected_lots: [
        {
          lot_id: 1,
          emission_rate_per_mj: 25,
          volume: "100",
        },
        {
          lot_id: 2,
          emission_rate_per_mj: 20.1,
          volume: "78.5",
        },
      ],
      fun: 1,
    })
  }
)

export const generateGetOperationDetail = (operation: Operation) => {
  return http.get("/tiruert/operations/{id}/", () => {
    return HttpResponse.json(operation)
  })
}

export const okGetOperationDetail = generateGetOperationDetail(operationCredit)
