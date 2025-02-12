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

// export const createOperation = (
//   entityId: number,
//   data: apiTypes["OperationCreateRequest"]
// ) => {
//   return api.POST("/tiruert/operations/", {
//     params: { query: { entity_id: entityId } },
//     body: data,
//   })
// }
