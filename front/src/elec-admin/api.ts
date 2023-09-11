import { api, Api } from "common/services/api"
import { ElecAdminProvisionCertificateFilter, ElecAdminProvisionCertificateQuery, ElecAdminSnapshot } from "./types"
import { ElecProvisionCertificatesData } from "elec/types"

export function getYears(entity_id: number) {
  return api.get<Api<number[]>>("/v5/admin/elec/years", {
    params: { entity_id },
  })
}

export function getSnapshot(entity_id: number, year: number) {
  return api.get<Api<ElecAdminSnapshot>>("/v5/admin/elec/snapshot", {
    params: { entity_id, year },
  })
}

export function importProvisionCertificates(entity_id: number, file: File) {
  return api.post("/v5/admin/elec/import-provision-certificates", {
    entity_id,
    file,
  })
}
const QUERY_RESET: Partial<ElecAdminProvisionCertificateQuery> = {
  limit: undefined,
  from_idx: undefined,
  sort_by: undefined,
  order: undefined,
}
export async function getProvisionCertificateFilters(field: ElecAdminProvisionCertificateFilter, query: ElecAdminProvisionCertificateQuery) {
  const params = { filter: field, ...query, ...QUERY_RESET }

  return api
    .get<Api<{ filter_values: string[] }>>("/v5/admin/elec/provision-certificate-filters", { params })
    .then((res) => res.data.data?.filter_values ?? [])

}


export function getProvisionCertificates(query: ElecAdminProvisionCertificateQuery) {
  return api.get<Api<ElecProvisionCertificatesData>>("/v5/admin/elec/provision-certificates", {
    params: query,
  })
}
