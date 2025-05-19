import { apiTypes } from "common/services/api-fetch.types"
import { api } from "common/services/api-fetch"
import {
  ElecOperationsFilter,
  ElecOperationsQuery,
  ElecOperationOrder,
} from "../types"

export const getOperationsFilters = (
  filter: string,
  query: ElecOperationsQuery
) => {
  return api.GET("/tiruert/elec-operations/filters/", {
    params: {
      query: {
        ...query,
        filter: filter as ElecOperationsFilter,
      },
    },
  })
}

export const getOperations = (query: ElecOperationsQuery) => {
  return api.GET("/tiruert/elec-operations/", {
    params: {
      query: {
        ...query,
        order_by:
          query.order_by && query.order_by.length > 0
            ? query.order_by
            : [ElecOperationOrder.ValueMinuscreated_at],
      },
    },
  })
}

export const patchOperation = (
  entityId: number,
  operationId: number,
  data: apiTypes["PatchedElecOperationUpdateRequest"]
) => {
  return api.PATCH("/tiruert/elec-operations/{id}/", {
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

export const createOperation = (
  entityId: number,
  data: apiTypes["ElecOperationInputRequest"]
) => {
  return api.POST("/tiruert/elec-operations/", {
    params: { query: { entity_id: entityId } },
    body: data,
  })
}

export const getOperationDetail = (entity_id: number, id: number) => {
  return api.GET(`/tiruert/elec-operations/{id}/`, {
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
  return api.DELETE(`/tiruert/elec-operations/{id}/`, {
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
  return api.POST(`/tiruert/elec-operations/{id}/accept/`, {
    params: {
      query: {
        entity_id,
      },
      path: { id: operation_id },
    },
  })
}

export const rejectOperation = (entity_id: number, operation_id: number) => {
  return api.POST(`/tiruert/elec-operations/{id}/reject/`, {
    params: {
      query: {
        entity_id,
      },
      path: { id: operation_id },
    },
  })
}
