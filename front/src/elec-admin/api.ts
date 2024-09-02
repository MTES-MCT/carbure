import { api, Api, download } from "common/services/api"
import {
  ElecChargePointsApplication,
  ElecMeterReadingsApplication,
  ElecProvisionCertificatesDetails,
  ElecTransferCertificatesDetails,
} from "elec/types"
import {
  ElecProvisionCertificatesData,
  ElecTransferCertificatesData,
} from "elec/types-cpo"
import {
  ElecAdminSnapshot,
} from "./types"
import { CBQUERY_RESET } from "common/hooks/query-builder"
import { ElecAdminProvisionCertificateQuery } from "./pages/provision-certificates/types"
import { ElecAdminTransferCertificateFilter, ElecAdminTransferCertificateQuery } from "./pages/transfer-certificates/types"

export function getYears(entity_id: number) {
  return api.get<Api<number[]>>("/elec/admin/years", {
    params: { entity_id },
  })
}

export function getSnapshot(entity_id: number, year: number) {
  return api.get<Api<ElecAdminSnapshot>>("/elec/admin/snapshot", {
    params: { entity_id, year },
  })
}

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
  field: ElecAdminTransferCertificateFilter,
  query: ElecAdminTransferCertificateQuery
) {
  const params = { filter: field, ...query, ...CBQUERY_RESET }
  return api
    .get<
      Api<{ filter_values: string[] }>
    >("/elec/admin/transfer-certificates/filters", { params })
    .then((res) => res.data.data?.filter_values ?? [])
}


//TO MOVE WHEN  /elec-charge-points created by Benjamin
export function downloadChargePointsApplicationDetails(
  entityId: number,
  companyId: number,
  applicationId: number
) {
  return download("/elec/admin/charge-points/application-details", {
    entity_id: entityId,
    company_id: companyId,
    application_id: applicationId,
    export: true,
  })
}

export function downloadChargePoints(entityId: number, companyId: number) {
  return download("/elec/admin/charge-points", {
    entity_id: entityId,
    company_id: companyId,
    export: true,
  })
}


export function getChargePointsApplications(
  entityId: number,
  companyId: number
) {
  return api.get<Api<ElecChargePointsApplication[]>>(
    "/elec/admin/charge-points/applications",
    {
      params: { entity_id: entityId, company_id: companyId },
    }
  )
}


export function getMeterReadingsApplications(
  entityId: number,
  companyId: number
) {
  return api.get<Api<ElecMeterReadingsApplication[]>>(
    "/elec/admin/meter-readings/applications",
    {
      params: { entity_id: entityId, company_id: companyId },
    }
  )
}

export function downloadMeterReadingsApplicationDetails(
  entityId: number,
  companyId: number,
  applicationId: number
) {
  return download("/elec/admin/meter-readings/application-details", {
    entity_id: entityId,
    company_id: companyId,
    application_id: applicationId,
    export: true,
  })
}
