import { CBQUERY_RESET } from "common/hooks/query-builder"
import { api, Api, download } from "common/services/api"
import {
  ElecTransferCertificatesData,
  ElecTransferCertificatesDetails,
} from "./types"
import { ElecTransferCertificateQuery } from "./types-cpo"
import { ElecOperatorSnapshot } from "./types-operator"

export function getOperatorYears(entity_id: number) {
  return api.get<Api<number[]>>("/elec/operator/years", {
    params: { entity_id },
  })
}

export function getOperatorSnapshot(entity_id: number, year: number) {
  return api.get<Api<ElecOperatorSnapshot>>("/elec/operator/snapshot", {
    params: { entity_id, year },
  })
}
export function getTransferCertificates(query: ElecTransferCertificateQuery) {
  return api.get<Api<ElecTransferCertificatesData>>(
    "/elec/operator/transfer-certificates",
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
  >("/elec/operator/transfer-certificate-details", {
    params: { entity_id, transfer_certificate_id },
  })
}

export function downloadTransferCertificates(
  query: ElecTransferCertificateQuery
) {
  return download("/elec/operator/transfer-certificates", {
    ...query,
    export: true,
  })
}

export async function getTransferCertificateFilters(
  field: string,
  query: ElecTransferCertificateQuery
) {
  const params = { filter: field, ...query, ...CBQUERY_RESET }

  return api
    .get<
      Api<{ filter_values: string[] }>
    >("/elec/operator/transfer-certificate-filters", { params })
    .then((res) => res.data.data?.filter_values ?? [])
}

export function rejectTransfer(
  entity_id: number,
  transfer_certificate_id: number,
  comment: string
) {
  return api.post("/elec/operator/reject-transfer-certificate", {
    entity_id,
    comment,
    transfer_certificate_id,
  })
}

export function acceptTransfer(
  entity_id: number,
  transfer_certificate_id: number
) {
  return api.post("/elec/operator/accept-transfer-certificate", {
    entity_id,
    transfer_certificate_id,
  })
}
