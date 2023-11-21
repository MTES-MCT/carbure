import { api, Api, download } from "common/services/api"
import { ElecChargingPointsApplication, ElecProvisionCertificatesDetails, ElecTransferCertificatesDetails } from "elec/types"
import { ElecProvisionCertificatesData, ElecTransferCertificatesData } from "elec/types-cpo"
import { ElecAdminProvisionCertificateFilter, ElecAdminProvisionCertificateQuery, ElecAdminSnapshot, ElecAdminTransferCertificateFilter, ElecAdminTransferCertificateQuery } from "./types"

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

export function getProvisionCertificateDetails(
  entity_id: number,
  provision_certificate_id: number
) {
  return api.get<Api<{ elec_provision_certificate: ElecProvisionCertificatesDetails }>>("/v5/admin/elec/provision-certificate-details", {
    params: { entity_id, provision_certificate_id },
  })
}

export function getProvisionCertificates(query: ElecAdminProvisionCertificateQuery) {
  return api.get<Api<ElecProvisionCertificatesData>>("/v5/admin/elec/provision-certificates", {
    params: query,
  })
}

export function getTransferCertificates(query: ElecAdminTransferCertificateQuery) {
  return api.get<Api<ElecTransferCertificatesData>>("/v5/admin/elec/transfer-certificates", {
    params: query,
  })
}

export function getTransferCertificateDetails(
  entity_id: number,
  transfer_certificate_id: number
) {
  return api.get<Api<{ elec_transfer_certificate: ElecTransferCertificatesDetails }>>("/v5/admin/elec/transfer-certificate-details", {
    params: { entity_id, transfer_certificate_id },
  })
}

export function downloadTransferCertificates(query: ElecAdminTransferCertificateQuery) {
  return download("/v5/admin/elec/transfer-certificates", { ...query, export: true })
}

export async function getTransferCertificateFilters(field: ElecAdminTransferCertificateFilter, query: ElecAdminTransferCertificateQuery) {
  const params = { filter: field, ...query, ...QUERY_RESET }
  return api
    .get<Api<{ filter_values: string[] }>>("/v5/admin/elec/transfer-certificate-filters", { params })
    .then((res) => res.data.data?.filter_values ?? [])
}

export function downloadChargingPointsApplicationDetails(entityId: number, companyId: number, applicationId: number) {
  return download("/v5/admin/elec/charging-points/application-details", {
    entity_id: entityId, company_id: companyId, application_id: applicationId, export: true
  })
}

export function downloadChargingPointsApplications(entityId: number, companyId: number) {
  return download("/v5/admin/elec/charging-points/applications", { entity_id: entityId, company_id: companyId, export: true })
}

export function getChargingPointsApplications(entityId: number, companyId: number) {
  return api.get<Api<ElecChargingPointsApplication[]>>("/v5/admin/elec/charging-points/applications", {
    params: { entity_id: entityId, company_id: companyId },
  })
}

export function acceptChargingPointsApplication(entityId: number, companyId: number, applicationId: number) {
  return api.post("/v5/admin/elec/charging-points/accept-application", {
    entity_id: entityId,
    company_id: companyId,
    application_id: applicationId,
  })
}


export function rejectChargingPointsApplication(entityId: number, companyId: number, applicationId: number) {
  return api.post("/v5/admin/elec/charging-points/reject-application", {
    entity_id: entityId,
    company_id: companyId,
    application_id: applicationId,
  })
}