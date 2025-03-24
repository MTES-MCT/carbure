import { api as apiFetch } from "common/services/api-fetch"
import { UserRole } from "common/types"

export function requestAccess(entity_id: number, role: UserRole, comment = "") {
  return apiFetch.POST("/user/request-access", {
    body: { entity_id, role, comment },
  })
}

export function revokeMyself(entity_id: number) {
  return apiFetch.POST("/user/revoke-access", {
    body: { entity_id },
  })
}
