import { api, Api, download } from "common/services/api"
import { ElecAuditorApplicationDetails, ElecAuditorApplicationsData, ElecAuditorApplicationsFilter, ElecAuditorApplicationsQuery, ElecAuditorApplicationsSnapshot } from "./types"
import { UploadCheckReportInfo } from "carbure/types"

export function getYears(entity_id: number) {
  return api.get<Api<number[]>>("/elec/audit/years", {
    params: { entity_id },
  })
}


// AUDIT
export function getSnapshot(entity_id: number, year: number) {
  return api.get<Api<ElecAuditorApplicationsSnapshot>>("/elec/audit/snapshot", {
    params: { entity_id, year },
  })
}


//CHARGE POINT
export function getApplications(query: ElecAuditorApplicationsQuery) {
  return api.get<Api<ElecAuditorApplicationsData>>("/elec/audit/applications", {
    params: query,
  })
}

const QUERY_RESET: Partial<ElecAuditorApplicationsQuery> = {
  limit: undefined,
  from_idx: undefined,
  sort_by: undefined,
  order: undefined,
}

export async function getFilters(field: ElecAuditorApplicationsFilter, query: ElecAuditorApplicationsQuery) {
  const params = { filter: field, ...query, ...QUERY_RESET }
  const result = await api
    .get<Api<string[]>>("/elec/audit/filters", { params })
    .then((res) => res.data.data ?? [])
  return result
}


export function getApplicationDetails(entityId: number, auditSampleId: number) {
  return api.get<Api<ElecAuditorApplicationDetails>>("/elec/audit/application-details", {
    params: { entity_id: entityId, audit_sample_id: auditSampleId },
  })
}


export function downloadSample(entityId: number, auditSampleId: number) {
  return download("/elec/audit/get-sample", { entity_id: entityId, audit_sample_id: auditSampleId, export: true })
}


export function checkAuditReport(entityId: number, auditSampleId: number, file: File) {
  return api.post<Api<UploadCheckReportInfo>>("/elec/audit/check-report", {
    entity_id: entityId,
    audit_sample_id: auditSampleId,
    file
  })
}

export function acceptAuditReport(entityId: number, auditSampleId: number, file: File) {
  return api.post("/elec/audit/accept-report", {
    entity_id: entityId,
    audit_sample_id: auditSampleId,
    file
  })
}