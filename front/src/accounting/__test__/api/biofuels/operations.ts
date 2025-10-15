import { http, HttpResponse } from "msw"
import { apiTypes } from "common/services/api-fetch.types"

export const okSimulateMinMax = http.post(
  "/api/tiruert/operations/simulate/min_max/",
  () => {
    return HttpResponse.json<apiTypes["SimulationMinMaxOutput"]>({
      min_avoided_emissions: 10,
      max_avoided_emissions: 50,
    })
  }
)

export const okSimulateMinMaxWithEqualValues = http.post(
  "/api/tiruert/operations/simulate/min_max/",
  () => {
    return HttpResponse.json<apiTypes["SimulationMinMaxOutput"]>({
      min_avoided_emissions: 10,
      max_avoided_emissions: 10.65,
    })
  }
)

export const okSimulateMinMaxWithZeroValues = http.post(
  "/api/tiruert/operations/simulate/min_max/",
  () => {
    return HttpResponse.json<apiTypes["SimulationMinMaxOutput"]>({
      min_avoided_emissions: 0.1,
      max_avoided_emissions: 0.2,
    })
  }
)
