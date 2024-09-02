import { CBQUERY_RESET } from "common/hooks/query-builder"
import { api, Api, download } from "common/services/api"
import {
  ElecTransferCertificatesDetails
} from "elec/types"
import { ElecTransferCertificatesData } from "elec/types-cpo"
import {
  ElecAdminTransferCertificateQuery
} from "./types"




export function getTransferCertificates(
  query: ElecAdminTransferCertificateQuery
) {
  return api.get<Api<ElecTransferCertificatesData>>(
    "/elec/admin/transfer-certificates",
    {
      params: query,
    }
  )
}


export function getTransferCertificateDetails(
  entity_id: number,
  transfer_certificate_id: number
) {
  return api.get<
    Api<{ elec_transfer_certificate: ElecTransferCertificatesDetails }>
  >("/elec/admin/transfer-certificates/transfer-certificate-details", {
    params: { entity_id, transfer_certificate_id },
  })
}

export function downloadTransferCertificates(
  query: ElecAdminTransferCertificateQuery
) {
  return download("/elec/admin/transfer-certificates", {
    ...query,
    export: true,
  })
}

export async function getTransferCertificateFilters(
  field: string,
  query: ElecAdminTransferCertificateQuery
) {
  const params = { filter: field, ...query, ...CBQUERY_RESET }
  return api
    .get<
      Api<{ filter_values: string[] }>
    >("/elec/admin/transfer-certificates/filters", { params })
    .then((res) => res.data.data?.filter_values ?? [])
}
