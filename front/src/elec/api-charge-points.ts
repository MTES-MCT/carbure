import { api, Api, download } from "common/services/api"
import { ElecChargePointsApplication } from "./types"
import { ChargePointsSnapshot } from "./types-charge-points"

export function getYears(entity_id: number) {
  return api.get<Api<number[]>>("/elec/charge-points/years", {
    params: { entity_id },
  })
}

export function getChargePointsSnapshot(entity_id: number, year: number) {
  return api.get<Api<ChargePointsSnapshot>>("/elec/charge-points/snapshot", {
    params: { entity_id, year },
  })
}

export function getChargePointsApplications(entity_id: number, year: number) {
  return api.get<Api<ElecChargePointsApplication[]>>(
    "/elec/charge-points/applications",
    {
      params: { entity_id, year },
    }
  )
}

export function downloadChargePointsApplicationDetails(
  entityId: number,
  applicationId: number
) {
  return download("/elec/charge-points/application-details", {
    entity_id: entityId,
    application_id: applicationId,
    export: true,
  })
}
