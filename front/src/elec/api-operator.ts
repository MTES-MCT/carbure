import { api, Api } from "common/services/api"
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


export async function getTransferCertificateFilters(field: ElecTransferCertificateFilter, query: ElecTransferCertificateQuery) {
  const params = { filter: field, ...query, ...QUERY_RESET }

  return api
    .get<Api<{ filter_values: string[] }>>("/v5/elec/operator/transfer-certificate-filters", { params })
    .then((res) => res.data.data?.filter_values ?? [])

}