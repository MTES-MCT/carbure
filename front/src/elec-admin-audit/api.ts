import { api, Api, download } from "common/services/api"
import { ElecChargePointsApplication } from "elec/types"
import { ElecAdminAuditFilter, ElecAdminAuditQuery, ElecAdminAuditSnapshot, ElecChargePointsApplicationsData } from "./types"

export function getYears(entity_id: number) {
  return api.get<Api<number[]>>("/elec/admin/audit/years", {
    params: { entity_id },
  })
}
export function getChargePointDetails(entity_id: number, charge_point_id: number) {
  return api.get<Api<ElecChargePointsApplication>>("/elec/admin/charge-points/application-details", {
    params: { entity_id, charge_point_id },
  })
}

export function getSnapshot(entity_id: number, year: number) {
  return api.get<Api<ElecAdminAuditSnapshot>>("/elec/admin/audit/snapshot", {
    params: { entity_id, year },
  })
}


export function getChargePointsApplications(query: ElecAdminAuditQuery) {
  return api.get<Api<ElecChargePointsApplicationsData>>("/elec/admin/audit/charge-points", {
    params: query,
  })
}

const QUERY_RESET: Partial<ElecAdminAuditQuery> = {
  limit: undefined,
  from_idx: undefined,
  sort_by: undefined,
  order: undefined,
}

export async function getElecAdminAuditFilters(field: ElecAdminAuditFilter, query: ElecAdminAuditQuery) {
  const params = { filter: field, ...query, ...QUERY_RESET }
  return api
    .get<Api<{ filter_values: string[] }>>("/elec/admin/audit/filters", { params })
    .then((res) => res.data.data?.filter_values ?? [])
}


export function getChargePointsApplicationDetails(entityId: number, applicationId: number) {
  return api.get<Api<ElecChargePointsApplication>>("/elec/admin/audit/charge-points/application_details", {
    params: { entity_id: entityId, application_id: applicationId },
  })

}

export function downloadChargePointsSample(entityId: number, applicationId: number) {
  return download("elec/admin/audit/charge-points/sample", { entity_id: entityId, application_id: applicationId })
}


export function startChargePointsApplicationAudit(entityId: number, applicationId: number) {
  return api.post("/elec/admin/audit/charge-points/start-audit", {
    entity_id: entityId,
    application_id: applicationId,
  })
}

export function acceptChargePointsApplication(entityId: number, applicationId: number, forceValidation: boolean) {
  return api.post("/elec/admin/charge-points/accept-application", {
    entity_id: entityId,
    application_id: applicationId,
    force_validation: forceValidation
  })
}


export function rejectChargePointsApplication(entityId: number, applicationId: number, forceRejection: boolean) {
  return api.post("/elec/admin/charge-points/reject-application", {
    entity_id: entityId,
    application_id: applicationId,
    force_rejection: forceRejection
  })
}