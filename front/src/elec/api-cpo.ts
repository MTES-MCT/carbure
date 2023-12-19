import { api, Api } from "common/services/api"
import { ElecCPOProvisionCertificateFilter, ElecCPOProvisionCertificateQuery, ElecCPOSnapshot, ElecTransferCertificateQuery, ElecProvisionCertificatesData, ElecTransferCertificatesData } from "./types-cpo"
import { EntityPreview } from "carbure/types"
import { extract } from "carbure/api"
import { ElecMeterReadingsApplication, ElecProvisionCertificatesDetails, ElecTransferCertificateFilter, ElecTransferCertificatesDetails, QUERY_RESET } from "./types"

export function getYears(entity_id: number) {
  return api.get<Api<number[]>>("/elec/cpo/years", { params: { entity_id } })
}

export function getSnapshot(entity_id: number, year: number) {
  return api.get<Api<ElecCPOSnapshot>>("/elec/cpo/snapshot", {
    params: { entity_id, year },
  })
}



export async function getProvisionCertificateFilters(field: ElecCPOProvisionCertificateFilter, query: ElecCPOProvisionCertificateQuery) {
  const params = { filter: field, ...query, ...QUERY_RESET }

  return api
    .get<Api<{ filter_values: string[] }>>("/elec/cpo/provision-certificate-filters", { params })
    .then((res) => res.data.data?.filter_values ?? [])

}

export function getProvisionCertificates(query: ElecCPOProvisionCertificateQuery) {
  return api.get<Api<ElecProvisionCertificatesData>>("/elec/cpo/provision-certificates", {
    params: query,
  })
}

export function getProvisionCertificateDetails(
  entity_id: number,
  provision_certificate_id: number
) {
  return api.get<Api<{ elec_provision_certificate: ElecProvisionCertificatesDetails }>>("/elec/cpo/provision-certificate-details", {
    params: { entity_id, provision_certificate_id },
  })
}

export function findClients(query?: string) {
  return api.get<Api<EntityPreview[]>>("/elec/cpo/clients", {
    params: { query },
  }).then(extract)
}



export function transferEnergy(
  entity_id: number,
  energy_mwh: number,
  client_id: number,
) {
  return api.post("/elec/cpo/create-transfer-certificate", {
    entity_id,
    energy_mwh,
    client_id
  })
}


export function getTransferCertificates(query: ElecTransferCertificateQuery) {
  return api.get<Api<ElecTransferCertificatesData>>("/elec/cpo/transfer-certificates", {
    params: query,
  })
}

export function getTransferCertificateDetails(
  entity_id: number,
  transfer_certificate_id: number
) {
  return api.get<Api<{ elec_transfer_certificate: ElecTransferCertificatesDetails }>>("/elec/cpo/transfer-certificate-details", {
    params: { entity_id, transfer_certificate_id },
  })
}


export async function getTransferCertificateFilters(field: ElecTransferCertificateFilter, query: ElecTransferCertificateQuery) {
  const params = { filter: field, ...query, ...QUERY_RESET }

  return api
    .get<Api<{ filter_values: string[] }>>("/elec/cpo/transfer-certificate-filters", { params })
    .then((res) => res.data.data?.filter_values ?? [])

}

export function cancelTransferCertificate(
  entity_id: number,
  transfer_certificate_id: number,
) {
  return api.post("/elec/cpo/cancel-transfer-certificate", {
    entity_id,
    transfer_certificate_id,
  })
}



// METER READINGS

export function getMeterReadingsApplications(entityId: number, companyId: number) {
  return api.get<Api<ElecMeterReadingsApplication[]>>("/elec/cpo/meter-readings/applications", {
    params: { entity_id: entityId, company_id: companyId },
  })
}