import { api, Api, download } from "common/services/api"
import { ElecChargingPointsApplication, ElecMeterReadingsApplication, ElecProvisionCertificatesDetails, ElecTransferCertificatesDetails } from "elec/types"
import { ElecProvisionCertificatesData, ElecTransferCertificatesData } from "elec/types-cpo"
import { ElecAdminProvisionCertificateFilter, ElecAdminProvisionCertificateQuery, ElecAdminSnapshot, ElecAdminTransferCertificateFilter, ElecAdminTransferCertificateQuery } from "./types"

export function getYears(entity_id: number) {
  return api.get<Api<number[]>>("/admin/elec/years", {
    params: { entity_id },
  })
}

export function getSnapshot(entity_id: number, year: number) {
  return api.get<Api<ElecAdminSnapshot>>("/admin/elec/snapshot", {
    params: { entity_id, year },
  })
}

export function importProvisionCertificates(entity_id: number, file: File) {
  return api.post("/admin/elec/import-provision-certificates", {
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
    .get<Api<{ filter_values: string[] }>>("/admin/elec/provision-certificate-filters", { params })
    .then((res) => res.data.data?.filter_values ?? [])

}

export function getProvisionCertificateDetails(
  entity_id: number,
  provision_certificate_id: number
) {
  return api.get<Api<{ elec_provision_certificate: ElecProvisionCertificatesDetails }>>("/admin/elec/provision-certificate-details", {
    params: { entity_id, provision_certificate_id },
  })
}

export function getProvisionCertificates(query: ElecAdminProvisionCertificateQuery) {
  return api.get<Api<ElecProvisionCertificatesData>>("/admin/elec/provision-certificates", {
    params: query,
  })
}

export function getTransferCertificates(query: ElecAdminTransferCertificateQuery) {
  return api.get<Api<ElecTransferCertificatesData>>("/admin/elec/transfer-certificates", {
    params: query,
  })
}

export function getTransferCertificateDetails(
  entity_id: number,
  transfer_certificate_id: number
) {
  return api.get<Api<{ elec_transfer_certificate: ElecTransferCertificatesDetails }>>("/admin/elec/transfer-certificate-details", {
    params: { entity_id, transfer_certificate_id },
  })
}

export function downloadTransferCertificates(query: ElecAdminTransferCertificateQuery) {
  return download("/admin/elec/transfer-certificates", { ...query, export: true })
}

export async function getTransferCertificateFilters(field: ElecAdminTransferCertificateFilter, query: ElecAdminTransferCertificateQuery) {
  const params = { filter: field, ...query, ...QUERY_RESET }
  return api
    .get<Api<{ filter_values: string[] }>>("/admin/elec/transfer-certificate-filters", { params })
    .then((res) => res.data.data?.filter_values ?? [])
}

export function downloadChargingPointsApplicationDetails(entityId: number, companyId: number, applicationId: number) {
  return download("/admin/elec/charging-points/application-details", {
    entity_id: entityId, company_id: companyId, application_id: applicationId, export: true
  })
}

export function downloadChargingPoints(entityId: number, companyId: number) {
  return download("/admin/elec/charging-points", { entity_id: entityId, company_id: companyId, export: true })
}

export function getChargingPointsApplications(entityId: number, companyId: number) {
  return api.get<Api<ElecChargingPointsApplication[]>>("/admin/elec/charging-points/applications", {
    params: { entity_id: entityId, company_id: companyId },
  })
}


export function acceptMeterReadingsApplication(entityId: number, companyId: number, applicationId: number) {
  return api.post("/admin/elec/meter-readings/accept-application", {
    entity_id: entityId,
    company_id: companyId,
    application_id: applicationId,
  })
}


export function rejectMeterReadingsApplication(entityId: number, companyId: number, applicationId: number) {
  return api.post("/admin/elec/meter-readings/reject-application", {
    entity_id: entityId,
    company_id: companyId,
    application_id: applicationId,
  })
}



//METER READINGS
export function getMeterReadingsApplications(entityId: number, companyId: number) {
  return api.get<Api<ElecMeterReadingsApplication[]>>("/admin/elec/meter-readings/applications", {
    params: { entity_id: entityId, company_id: companyId },
  })
}

export function downloadMeterReadingsApplicationDetails(entityId: number, companyId: number, applicationId: number) {
  return download("/admin/elec/meter-readings/application-details", {
    entity_id: entityId, company_id: companyId, application_id: applicationId, export: true
  })
}

export function acceptChargingPointsApplication(entityId: number, companyId: number, applicationId: number) {
  return api.post("/admin/elec/meter-readings/accept-application", {
    entity_id: entityId,
    company_id: companyId,
    application_id: applicationId,
  })
}


export function rejectChargingPointsApplication(entityId: number, companyId: number, applicationId: number) {
  return api.post("/admin/elec/meter-readings/reject-application", {
    entity_id: entityId,
    company_id: companyId,
    application_id: applicationId,
  })
}