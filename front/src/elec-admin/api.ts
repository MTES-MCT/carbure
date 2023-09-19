import { api, Api } from "common/services/api"
import { ElecAdminProvisionCertificateFilter, ElecAdminProvisionCertificateQuery, ElecAdminSnapshot, ElecAdminTransferCertificateFilter, ElecAdminTransferCertificateQuery } from "./types"
import { ElecProvisionCertificatesData, ElecTransferCertificatesData } from "elec/types"

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
  console.log('getProvisionCertificates')
  return api.get<Api<ElecProvisionCertificatesData>>("/v5/admin/elec/provision-certificates", {
    params: query,
  })
}

export function getTransferCertificates(query: ElecAdminTransferCertificateQuery) {
  return api.get<Api<ElecTransferCertificatesData>>("/v5/admin/elec/transfer-certificates", {
    params: query,
  })
}

export async function getTransferCertificateFilters(field: ElecAdminTransferCertificateFilter, query: ElecAdminTransferCertificateQuery) {
  const params = { filter: field, ...query, ...QUERY_RESET }

  return api
    .get<Api<{ filter_values: string[] }>>("/v5/admin/elec/transfer-certificate-filters", { params })
    .then((res) => res.data.data?.filter_values ?? [])

}