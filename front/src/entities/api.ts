import api from "common/services/api"
import { Entity, UserRightRequest, UserRightStatus } from "carbure/types"
import { ProductionSiteDetails } from "common/types"
import { EntityDeliverySite } from "settings/hooks/use-delivery-sites"

export interface EntityDetails {
  entity: Entity
  users: number
  requests: number
  depots: number
  production_sites: number
  certificates: number
  double_counting: number
  double_counting_requests: number
}

export function getEntities(): Promise<EntityDetails[]> {
  return api.get("/admin/entities")
}

export function getEntityDetails(entity_id: number): Promise<Entity> {
  return api.get("/admin/entities/details", { entity_id })
}

export function getEntityDepots(
  entity_id: number
): Promise<EntityDeliverySite[]> {
  return api.get("/admin/entities/depots", { entity_id })
}

export function getEntityProductionSites(
  entity_id: number
): Promise<ProductionSiteDetails[]> {
  return api.get("/admin/entities/production_sites", { entity_id })
}

export function getEntityCertificates(entity_id: number): Promise<any[]> {
  return api.get("/admin/entities/certificates", { entity_id })
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
