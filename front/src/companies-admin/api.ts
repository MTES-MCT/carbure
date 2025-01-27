import { api as apiFetch } from "common/services/api-fetch"
import { UserRightStatus, EntityType, UserRole } from "carbure/types"

export function getCompanies(entity_id: number) {
  return apiFetch.GET("/entities/", {
    params: { query: { entity_id } },
  })
}

export function addCompany(
  entity_id: number,
  name: string,
  entity_type: EntityType,
  has_saf: boolean,
  has_elec: boolean
) {
  console.log("OKOKOK 61")
  return apiFetch.POST("/entities/", {
    params: { query: { entity_id } },
    body: {
      name,
      has_saf,
      has_elec,
    },
  })
}

export function getCompanyDetails(entity_id: number, company_id: number) {
  console.log("OKOKOK 62", entity_id)
  return apiFetch.GET("/entities/{id}/", {
    params: {
      path: { id: company_id },
      query: { entity_id },
    },
  })
}

export function getCompanyDepots(entity_id: number, company_id: number) {
  console.log("OKOKOK 63")
  return apiFetch.GET("/entities/depots/", {
    params: { query: { entity_id, company_id } },
  })
}

export function getCompanyProductionSites(
  entity_id: number,
  company_id: number
) {
  console.log("OKOKOK 64")
  return apiFetch.GET("/entities/production-sites/", {
    params: { query: { entity_id, company_id } },
  })
}

export function getUsersRightRequests(
  entity_id: number,
  query: string,
  company_id: number,
  statuses?: UserRightStatus[]
) {
  console.log("OKOKOK 65")
  return apiFetch.GET("/entities/users/rights-requests/", {
    params: { query: { entity_id, q: query, company_id, statuses } },
  })
}

export function updateUsersRights(
  request_id: number,
  entity_id: number,
  status: UserRightStatus
) {
  console.log("OKOKOK 66")
  return apiFetch.POST("/entities/users/update-right-request/", {
    params: { query: { entity_id } },
    body: { id: request_id, status },
  })
}
export function updateUserRole(
  request_id: number,
  entity_id: number,
  role: UserRole
) {
  console.log("OKOKOK 67")
  return apiFetch.POST("/entities/users/update-user-role/", {
    params: { query: { entity_id } },
    body: { request_id, role },
  })
}

export function getEntityCertificates(entity_id: number, company_id?: number) {
  console.log("OKOKOK 68", company_id, "remove admin permission bug")
  return apiFetch.GET("/entities/certificates/", {
    params: { query: { entity_id, company_id } },
  })
}

export function checkEntityCertificate(
  entity_id: number,
  entity_certificate_id: number
) {
  console.log("OKOKOK 69")
  return apiFetch.POST("/entities/certificates/check-entity/", {
    params: { query: { entity_id } },
    body: { entity_certificate_id },
  })
}

export function rejectEntityCertificate(
  entity_id: number,
  entity_certificate_id: number
) {
  console.log("OKOKOK 70")
  return apiFetch.POST("/entities/certificates/reject-entity/", {
    params: { query: { entity_id } },
    body: { entity_certificate_id },
  })
}

export function enableCompany(entity_id: number, company_id: number) {
  console.log("OKOKOK 71")
  return apiFetch.POST("/entities/{id}/enable/", {
    params: {
      path: { id: company_id },
      query: { entity_id },
    },
  })
}
