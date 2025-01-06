import { api as apiFetch } from "common/services/api-fetch"
import { UserRole } from "carbure/types"

export function getEntityRights(entity_id: number) {
  console.log("OKOKOKOKOK 11")
  return apiFetch.GET("/entities/users/", {
    params: { query: { entity_id } },
  })
}

export function revokeUserRights(entity_id: number, email: string) {
  console.log("VERYUNSURE 12")
  return apiFetch.POST("/entities/users/revoke-access/", {
    params: { query: { entity_id } },
    body: { email },
  })
}

export function acceptUserRightsRequest(entity_id: number, request_id: number) {
  console.log("VERYUNSURE 13")
  return apiFetch.POST("/entities/users/grant-access/", {
    params: { query: { entity_id } },
    body: { request_id },
  })
}

export function changeUserRole(
  entity_id: number,
  email: string,
  role: UserRole
) {
  console.log("VERYUNSURE 14")
  return apiFetch.POST("/entities/users/change-role/", {
    params: { query: { entity_id } },
    body: { email, role },
  })
}

export function inviteUser(entity_id: number, email: string, role: UserRole) {
  console.log("VERYUNSURE 15")
  return apiFetch.POST("/entities/users/invite-user/", {
    params: { query: { entity_id } },
    body: { email, role },
  })
}
