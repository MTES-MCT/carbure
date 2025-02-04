import { api as apiFetch } from "common/services/api-fetch"
import { UserRole } from "carbure/types"

export function getEntityRights(entity_id: number) {
  return apiFetch.GET("/entities/users/entity-rights-requests/", {
    params: { query: { entity_id } },
  })
}

export function revokeUserRights(entity_id: number, email: string) {
  return apiFetch.POST("/entities/users/revoke-access/", {
    params: { query: { entity_id } },
    body: { email },
  })
}

export function acceptUserRightsRequest(entity_id: number, request_id: number) {
  return apiFetch.POST("/entities/users/accept-user/", {
    params: { query: { entity_id } },
    body: { request_id },
  })
}

export function changeUserRole(
  entity_id: number,
  email: string,
  role: UserRole
) {
  return apiFetch.POST("/entities/users/change-role/", {
    params: { query: { entity_id } },
    body: { email, role },
  })
}

export function inviteUser(entity_id: number, email: string, role: UserRole) {
  return apiFetch.POST("/entities/users/invite-user/", {
    params: { query: { entity_id } },
    body: { email, role },
  })
}
