import api from "common/services/api"
import { api as apiFetch } from "common/services/api-fetch"
import { UserRole } from "carbure/types"

export function requestAccess(entity_id: number, role: UserRole, comment = "") {
  return apiFetch.POST("/user/request-access", {
    body: { entity_id, role, comment },
  })
}

export function revokeMyself(entity_id: number) {
  return api.post("/user/revoke-access", { entity_id })
}
