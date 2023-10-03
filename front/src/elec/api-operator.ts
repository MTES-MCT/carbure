import { api, Api, download } from "common/services/api"
import { ElecOperatorSnapshot } from "./types-operator"
import { ElecTransferCertificateQuery } from "./types-cpo"
import { ElecTransferCertificateFilter, ElecTransferCertificatesData, QUERY_RESET } from "./types"

export function getOperatorYears(entity_id: number) {
  return api.get<Api<number[]>>("/v5/elec/operator/years", { params: { entity_id } })
}

export function getOperatorSnapshot(entity_id: number, year: number) {
  return api.get<Api<ElecOperatorSnapshot>>("/v5/elec/operator/snapshot", {
    params: { entity_id, year },
  })
}
export function getTransferCertificates(query: ElecTransferCertificateQuery) {
  return api.get<Api<ElecTransferCertificatesData>>("/v5/elec/operator/transfer-certificates", {
    params: query,
  })
}

export function downloadTransferCertificates(query: ElecTransferCertificateQuery) {
  return download("/v5/elec/operator/transfer-certificates", { ...query, export: true })
}


export async function getTransferCertificateFilters(field: ElecTransferCertificateFilter, query: ElecTransferCertificateQuery) {
  const params = { filter: field, ...query, ...QUERY_RESET }

  return api
    .get<Api<{ filter_values: string[] }>>("/v5/elec/operator/transfer-certificate-filters", { params })
    .then((res) => res.data.data?.filter_values ?? [])

}

export function rejectTransfer(
  entity_id: number,
  transfer_certificate_id: number,
  comment: string
) {
  return api.post("/v5/elec/operator/reject-transfer-certificate", {
    entity_id,
    comment,
    transfer_certificate_id,
  })
}


export function acceptTransfer(entity_id: number, transfer_certificate_id: number) {
  return api.post("/v5/elec/operator/accept-transfer-certificate", {
    entity_id,
    transfer_certificate_id,
  })
}