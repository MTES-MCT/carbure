import api, { Api } from "common/services/api"
import {
  Entity,
  UserRightRequest,
  UserRightStatus,
  ProductionSiteDetails,
  EntityDepot,
  EntityCertificate,
  EntityType,
} from "carbure/types"
import { EntityDetails } from "./types"

export function getCompanies(entity_id: number) {
  return api.get<Api<EntityDetails[]>>("/v5/admin/entities", {
    params: { entity_id },
  })
}

export function addCompany(
  entity_id: number,
  name: string,
  entity_type: EntityType,
  has_saf: boolean
) {
  return api.post("/v5/admin/create-entity", {
    entity_id,
    name,
    entity_type,
    has_saf,
  })
}

export function getCompanyDetails(entity_id: number, company_id: number) {
  return api.get<Api<Entity>>("/v5/admin/entities/details", {
    params: { entity_id, company_id },
  })
}

export function getCompanyDepots(entity_id: number, company_id: number) {
  return api.get<Api<EntityDepot[]>>("/v5/admin/entities/depots", {
    params: { entity_id, company_id },
  })
}

export function getCompanyProductionSites(entity_id: number, company_id: number) {
  return api.get<Api<ProductionSiteDetails[]>>(
    "/v5/admin/entities/production_sites",
    {
      params: { entity_id, company_id },
    }
  )
}

export function getUsersRightRequests(
  entity_id: number,
  query: string,
  company_id: number,
  statuses?: UserRightStatus[]
) {
  return api.get<Api<UserRightRequest[]>>("/v5/admin/entities/users/rights-requests", {
    params: { entity_id, q: query, company_id, statuses },
  })
}

export function updateUsersRights(user_id: number, entity_id: number, status?: UserRightStatus,) {
  return api.post("/v5/admin/entities/users/update-right-request", {
    id: user_id,
    entity_id,
    status
  })
}

export function getEntityCertificates(entity_id: number, company_id?: number) {
  return api.get<Api<EntityCertificate[]>>("/v5/admin/entities/certificates", {
    params: { entity_id, company_id },
  })
}

export function checkEntityCertificate(entity_id: number, entity_certificate_id: number) {
  return api.post("v5/admin/entities/certificates/check", { entity_id, entity_certificate_id })
}

export function rejectEntityCertificate(entity_id: number, entity_certificate_id: number) {
  return api.post("v5/admin/entities/certificates/reject", { entity_id, entity_certificate_id })
}
