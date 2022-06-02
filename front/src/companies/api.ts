import api, { Api } from "common/services/api"
import {
  Entity,
  UserRightRequest,
  UserRightStatus,
  ProductionSiteDetails,
  EntityDepot,
  EntityCertificate,
} from "carbure/types"
import { EntityDetails } from "./types"

export function getEntities() {
  return api.get<Api<EntityDetails[]>>("/v3/admin/entities")
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

export function getEntityCertificates(entity_id?: number) {
  return api.get<Api<EntityCertificate[]>>("/admin/entity-certificates", {
    params: { entity_id },
  })
}

export function checkEntityCertificate(entity_certificate_id: number) {
  return api.post("admin/entity-certificates/check", { entity_certificate_id })
}

export function rejectEntityCertificate(entity_certificate_id: number) {
  return api.post("admin/entity-certificates/reject", { entity_certificate_id })
}
