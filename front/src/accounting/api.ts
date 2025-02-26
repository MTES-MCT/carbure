import { apiTypes } from "common/services/api-fetch.types"
import { api } from "common/services/api-fetch"

export const patchOperation = (
  entityId: number,
  operationId: number,
  data: apiTypes["PatchedOperationUpdateRequest"]
) => {
  return api.PATCH("/tiruert/operations/{id}/", {
    params: {
      query: {
        entity_id: entityId,
      },
      path: {
        id: operationId,
      },
    },
    body: data,
  })
}

export const simulateMinMax = (
  entityId: number,
  {
    biofuel,
    customs_category,
    debited_entity,
    target_volume,
    unit,
  }: apiTypes["SimulationInputRequest"]
) => {
  return api.POST("/tiruert/operations/simulate/min_max/", {
    params: { query: { entity_id: entityId } },
    body: {
      biofuel,
      customs_category,
      debited_entity,
      target_volume,
      unit,
    },
  })
}

// Get the lots that can be used to create an operation
export const simulate = (
  entityId: number,
  data: apiTypes["SimulationInputRequest"]
) => {
  return api.POST("/tiruert/operations/simulate/", {
    params: { query: { entity_id: entityId } },
    body: data,
  })
}

export const createOperation = (
  entityId: number,
  data: apiTypes["OperationInputRequest"]
) => {
  return api.POST("/tiruert/operations/", {
    params: { query: { entity_id: entityId } },
    body: data,
    bodySerializer: undefined,
  })
}
