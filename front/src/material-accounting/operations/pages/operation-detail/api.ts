import { api as apiFetch } from "common/services/api-fetch"

// missing entity id
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
