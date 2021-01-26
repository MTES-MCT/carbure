import api from "common/services/api"
import { Entity, UserRightRequest, UserRightStatus } from "common/types"

export interface EntityDetails {
  entity: Entity
  users: number
  requests: number
  depots: number
  production_sites: number
  certificates_2bs: number
  certificates_iscc: number
}

export function getEntities(query: string): Promise<EntityDetails[]> {
  return api.get("/admin/entities", { q: query })
}

export function getEntityDetails(entity_id: number): Promise<Entity> {
  return api.get("/admin/entities/details", { entity_id })
}

export function getUsers(query: string, entity_id: number): Promise<any[]> {
  return api.get("/admin/users", { q: query, entity_id })
}

export function getUsersRightRequests(
  query: string,
  entity_id: number,
  statuses?: UserRightStatus[]
): Promise<UserRightRequest[]> {
  return api.get("/admin/users/rights-requests", {
    q: query,
    entity_id,
    statuses,
  })
}

export function updateUsersRights(user_id: number, status?: UserRightStatus) {
  return api.post("/admin/users/update-right-request", {
    id: user_id,
    status,
  })
}
