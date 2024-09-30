import { CBQUERY_RESET } from "common/hooks/query-builder"
import { api, Api } from "common/services/api"
import { ElecProvisionCertificatesDetails } from "elec/types"
import { ElecProvisionCertificatesData } from "elec/types-cpo"
import { ElecAdminProvisionCertificateQuery } from "./types"

export function importProvisionCertificates(entity_id: number, file: File) {
  return api.post("/elec/admin/provision-certificates/import-certificates", {
    entity_id,
    file,
  })
}

export async function getProvisionCertificateFilters(
  field: string,
  query: ElecAdminProvisionCertificateQuery
) {
  const params = { filter: field, ...query, ...CBQUERY_RESET }

  return api
    .get<
      Api<{ filter_values: string[] }>
    >("/elec/admin/provision-certificates/filters", { params })
    .then((res) => res.data.data?.filter_values ?? [])
}

export function getProvisionCertificateDetails(
  entity_id: number,
  provision_certificate_id: number
) {
  return api.get<
    Api<{ elec_provision_certificate: ElecProvisionCertificatesDetails }>
  >("/elec/admin/provision-certificates/provision-certificate-details", {
    params: { entity_id, provision_certificate_id },
  })
}

export function getProvisionCertificates(
  query: ElecAdminProvisionCertificateQuery
) {
  return api.get<Api<ElecProvisionCertificatesData>>(
    "/elec/admin/provision-certificates",
    {
      params: query,
    }
  )
}
