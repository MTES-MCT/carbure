import { api as apiFetch } from "common/services/api-fetch"

export const getOperationDetail = (entity_id: number, id: number) => {
  return apiFetch.GET(`/tiruert/operations/{id}/`, {
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
  return apiFetch.DELETE(`/tiruert/operations/{id}/`, {
    params: {
      query: {
        entity_id: entity_id.toString(),
      },
      path: {
        id: operation_id,
      },
    },
  })
}
