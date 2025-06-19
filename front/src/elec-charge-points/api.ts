import { api, Api, download } from "common/services/api"
import {
  ChargePointsSnapshot,
  ElecChargePointsApplication,
  ElecChargePointsApplicationCheckInfo,
  ElecMeterReadingsApplication,
  ElecMeterReadingsApplicationCheckInfo,
  ElecMeterReadingsApplicationsResponse,
} from "../elec-charge-points/types"

export function getYears(entity_id: number) {
  return api.get<Api<number[]>>("/elec/cpo/charge-point-years", {
    params: { entity_id },
  })
}

export function getChargePointsSnapshot(entity_id: number) {
  return api.get<Api<ChargePointsSnapshot>>("/elec/cpo/charge-point-snapshot", {
    params: { entity_id, category: "charge_point" },
  })
}

// CHARGE POINTS

export function getChargePointsApplications(
  entity_id: number,
  companyId: number
) {
  return api.get<Api<ElecChargePointsApplication[]>>(
    "/elec/cpo/charge-points/applications",
    {
      params: { entity_id, company_id: companyId },
    }
  )
}

export function downloadChargePoints(entityId: number, companyId: number) {
  return download("/elec/cpo/charge-points", {
    entity_id: entityId,
    company_id: companyId,
    export: true,
  })
}

export function checkChargePointsApplication(entity_id: number, file: File) {
  return api.post<Api<ElecChargePointsApplicationCheckInfo>>(
    "/elec/cpo/charge-points/check-application",
    { entity_id, file }
  )
}

export function downloadChargePointsApplicationDetails(
  entityId: number,
  applicationId: number
) {
  return download("/elec/cpo/charge-points/application-details", {
    entity_id: entityId,
    application_id: applicationId,
    export: true,
  })
}

export function addChargePoints(entity_id: number, file: File) {
  return api.post("/elec/cpo/charge-points/add-application", {
    entity_id,
    file,
  })
}

// METER READINGS

export function getMeterReadingsApplications(
  entityId: number,
  companyId: number
) {
  return api.get<Api<ElecMeterReadingsApplicationsResponse>>(
    "/elec/cpo/meter-readings/applications",
    {
      params: { entity_id: entityId, company_id: companyId },
    }
  )
}

export function getMeterReadingsTemplate(entityId: number, companyId: number) {
  return api.get<Api<ElecMeterReadingsApplication[]>>(
    "/elec/cpo/meter-readings/application-template",
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
  return download("/elec/cpo/meter-readings/application-details", {
    entity_id: entityId,
    application_id: applicationId,
    export: true,
  })
}

export function checkMeterReadingsApplication(
  entity_id: number,
  file: File,
  quarter?: number,
  year?: number
) {
  return api.post<Api<ElecMeterReadingsApplicationCheckInfo>>(
    "/elec/cpo/meter-readings/check-application",
    { entity_id, file, quarter, year }
  )
}

export function addMeterReadings(
  entity_id: number,
  file: File,
  quarter?: number,
  year?: number
) {
  return api.post("/elec/cpo/meter-readings/add-application", {
    entity_id,
    file,
    quarter,
    year,
  })
}
