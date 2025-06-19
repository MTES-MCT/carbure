import { api, Api, download } from "common/services/api"
import {
  ElecChargePointsApplication,
  ElecMeterReadingsApplication,
} from "elec/types"

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
