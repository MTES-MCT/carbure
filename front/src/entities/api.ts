import api, { Api } from "common-v2/services/api"
import { Entity, UserRightRequest, UserRightStatus } from "carbure/types"
import { ProductionSiteDetails, EntityDepot } from "common-v2/types"

export interface EntityDetails {
  entity: Entity
  users: number
  requests: number
  depots: number
  production_sites: number
  certificates: number
  certificates_pending: number
  double_counting: number
  double_counting_requests: number
}

export function getEntities(): Promise<EntityDetails[]> {
  return api.get("/v3/admin/entities")
}

export function getEntityDetails(entity_id: number) {
  return api.get<Api<Entity>>("/v3/admin/entities/details", {
    params: { entity_id },
  })
}

export function getEntityDepots(entity_id: number) {
  return api.get<Api<EntityDepot[]>>("/v3/admin/entities/depots", {
    params: { entity_id },
  })
}

export function getEntityProductionSites(entity_id: number) {
  return api.get<Api<ProductionSiteDetails[]>>(
    "/v3/admin/entities/production_sites",
    {
      params: { entity_id },
    }
  )
}

export function getUsers(query: string, entity_id: number) {
  return api.get<Api<UserRightRequest[]>>("/v3/admin/users", {
    params: { q: query, entity_id },
  })
}

export function getUsersRightRequests(
  query: string,
  entity_id: number,
  statuses?: UserRightStatus[]
) {
  return api.get<Api<UserRightRequest[]>>("/v3/admin/users/rights-requests", {
    params: { q: query, entity_id, statuses },
  })
}

export function updateUsersRights(user_id: number, status?: UserRightStatus) {
  return api.post("/v3/admin/users/update-right-request", {
    id: user_id,
    status,
  })
}
