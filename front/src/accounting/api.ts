import { apiTypes } from "common/services/api-fetch.types"
import { api } from "common/services/api-fetch"
import { OperationsFilter, OperationsQuery } from "./types"

export const getOperationsFilters = (
  filter: string,
  query: OperationsQuery
) => {
  return api.GET("/tiruert/operations/filters/", {
    params: {
      query: {
        ...query,
        filter: filter as OperationsFilter,
      },
    },
  })
}

export const getOperations = (query: OperationsQuery) => {
  return api.GET("/tiruert/operations/", {
    params: {
      query,
    },
  })
}

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
  }: apiTypes["SimulationInputRequest"]
) => {
  return api.POST("/tiruert/operations/simulate/min_max/", {
    params: { query: { entity_id: entityId } },
    body: {
      biofuel,
      customs_category,
      debited_entity,
      target_volume,
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
    bodySerializer: (data) => JSON.stringify(data), // Body contains array of objects, our backend could not handle it in a formData
  })
}

export const getOperationDetail = (entity_id: number, id: number) => {
  return api.GET(`/tiruert/operations/{id}/`, {
    params: {
      query: {
        entity_id,
      },
      path: {
        id,
      },
    },
  })
}

export const deleteOperation = (entity_id: number, operation_id: number) => {
  return api.DELETE(`/tiruert/operations/{id}/`, {
    params: {
      query: {
        entity_id,
      },
      path: {
        id: operation_id,
      },
    },
  })
}

export const acceptOperation = (entity_id: number, operation_id: number) => {
  return api.POST(`/tiruert/operations/{id}/accept/`, {
    params: {
      query: {
        entity_id,
      },
      path: { id: operation_id },
    },
  })
}

export const rejectOperation = (entity_id: number, operation_id: number) => {
  return api.POST(`/tiruert/operations/{id}/reject/`, {
    params: {
      query: {
        entity_id,
      },
      path: { id: operation_id },
    },
  })
}
