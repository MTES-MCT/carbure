import { api, Api } from "common/services/api"
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
    .get<Api<{ filter_values: string[] }>>("/elec/admin/transfer-certificate-filters", { params })
    .then((res) => res.data.data?.filter_values ?? [])
}
