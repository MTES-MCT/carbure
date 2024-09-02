import { CBQUERY_RESET } from "common/hooks/query-builder"
import { api, Api, download } from "common/services/api"
import {
  ElecChargePointsApplication,
  ElecChargePointsApplicationDetails,
  ElecMeterReadingsApplicationDetails
} from "elec/types"
import {
  ElecAdminAuditQuery,
  ElecAdminAuditSnapshot,
  ElecApplicationSample,
  ElecChargePointsApplicationsData,
  ElecMeterReadingsApplicationsData
} from "./types"

export function getYears(entity_id: number) {
  return api.get<Api<number[]>>("/elec/admin/audit/years", {
    params: { entity_id },
  })
}
export function getChargePointDetails(
  entity_id: number,
  charge_point_id: number
) {
  return api.get<Api<ElecChargePointsApplication>>(
    "/elec/admin/charge-points/application-details",
    {
      params: { entity_id, charge_point_id },
    }
  )
}

// AUDIT
export function getSnapshot(entity_id: number, year: number) {
  return api.get<Api<ElecAdminAuditSnapshot>>("/elec/admin/audit/snapshot", {
    params: { entity_id, year },
  })
}

//CHARGE POINT
export function getChargePointsApplications(query: ElecAdminAuditQuery) {
  return api.get<Api<ElecChargePointsApplicationsData>>(
    "/elec/admin/audit/charge-points/applications",
    {
      params: query,
    }
  )
}



export async function getElecAdminAuditChargePointsApplicationsFilters(
  field: string,
  query: ElecAdminAuditQuery
) {
  const params = { filter: field, ...query, ...CBQUERY_RESET }
  const result = await api
    .get<Api<string[]>>("/elec/admin/audit/charge-points/filters", { params })
    .then((res) => res.data.data ?? [])
  return result
}

export function getChargePointsApplicationDetails(
  entityId: number,
  applicationId: number
) {
  return api.get<Api<ElecChargePointsApplicationDetails>>(
    "/elec/admin/audit/charge-points/application-details",
    {
      params: { entity_id: entityId, application_id: applicationId },
    }
  )
}

export function generateChargePointsAuditSample(
  entityId: number,
  applicationId: number,
  percentage: number
) {
  return api.post<Api<ElecApplicationSample>>(
    "/elec/admin/audit/charge-points/generate-sample",
    {
      entity_id: entityId,
      application_id: applicationId,
      percentage: percentage,
    }
  )
}

export function downloadChargePointsSample(
  entityId: number,
  applicationId: number
) {
  return download("/elec/admin/audit/charge-points/get-sample", {
    entity_id: entityId,
    application_id: applicationId,
    export: true,
  })
}

export function startChargePointsApplicationAudit(
  entityId: number,
  applicationId: number
) {
  return api.post("/elec/admin/audit/charge-points/start-audit", {
    entity_id: entityId,
    application_id: applicationId,
  })
}

export function acceptChargePointsApplication(
  entityId: number,
  applicationId: number,
  forceValidation: boolean
) {
  return api.post("/elec/admin/audit/charge-points/accept-application", {
    entity_id: entityId,
    application_id: applicationId,
    force_validation: forceValidation,
  })
}

export function rejectChargePointsApplication(
  entityId: number,
  applicationId: number,
  forceRejection: boolean
) {
  return api.post("/elec/admin/audit/charge-points/reject-application", {
    entity_id: entityId,
    application_id: applicationId,
    force_rejection: forceRejection,
  })
}

//METER READINGS
export function getMeterReadingsApplications(query: ElecAdminAuditQuery) {
  return api.get<Api<ElecMeterReadingsApplicationsData>>(
    "/elec/admin/audit/meter-readings/applications",
    {
      params: query,
    }
  )
}

export async function getElecAdminAuditMeterReadingsApplicationsFilters(
  filter: string,
  query: ElecAdminAuditQuery
) {
  const params = { filter, ...query, ...CBQUERY_RESET }
  const result = await api
    .get<Api<string[]>>("/elec/admin/audit/meter-readings/filters", { params })
    .then((res) => res.data.data ?? [])
  return result
}

export function getMeterReadingsApplicationDetails(
  entityId: number,
  applicationId: number
) {
  return api.get<Api<ElecMeterReadingsApplicationDetails>>(
    "/elec/admin/audit/meter-readings/application-details",
    {
      params: { entity_id: entityId, application_id: applicationId },
    }
  )
}

export function generateMeterReadingsAuditSample(
  entityId: number,
  applicationId: number,
  percentage: number
) {
  return api.post<Api<ElecApplicationSample>>(
    "/elec/admin/audit/meter-readings/generate-sample",
    {
      entity_id: entityId,
      application_id: applicationId,
      percentage: percentage,
    }
  )
}

export function downloadMeterReadingsSample(
  entityId: number,
  applicationId: number
) {
  return download("/elec/admin/audit/meter-readings/get-sample", {
    entity_id: entityId,
    application_id: applicationId,
    export: true,
  })
}

export function downloadMeterReadingsApplication(
  entityId: number,
  applicationId: number,
  sample = false
) {
  return download("/elec/admin/audit/meter-readings/application-details", {
    entity_id: entityId,
    application_id: applicationId,
    export: true,
    sample: sample,
  })
}

export function startMeterReadingsApplicationAudit(
  entityId: number,
  applicationId: number
) {
  return api.post("/elec/admin/audit/meter-readings/start-audit", {
    entity_id: entityId,
    application_id: applicationId,
  })
}

export function acceptMeterReadingsApplication(
  entityId: number,
  applicationId: number,
  forceValidation: boolean
) {
  return api.post("/elec/admin/audit/meter-readings/accept-application", {
    entity_id: entityId,
    application_id: applicationId,
    force_validation: forceValidation,
  })
}

export function rejectMeterReadingsApplication(
  entityId: number,
  applicationId: number,
  forceRejection: boolean
) {
  return api.post("/elec/admin/audit/meter-readings/reject-application", {
    entity_id: entityId,
    application_id: applicationId,
    force_rejection: forceRejection,
  })
}



export function downloadAuditReport(
  entityId: number,
  sampleId: number
) {
  return download("/elec/admin/audit/get-report", {
    entity_id: entityId,
    audit_sample_id: sampleId,
    export: true,
  })
}
