import { api, Api } from "common/services/api"
import { ElecChargingPointsApplication } from "elec/types"

export function getYears(entity_id: number) {
  return api.get<Api<number[]>>("/elec/admin/audit/years", {
    params: { entity_id },
  })
}
export function getChargePointDetails(entity_id: number, charging_point_id: number) {
  return api.get<Api<ElecChargingPointsApplication>>("/elec/admin/charging-points/application-details", {
    params: { entity_id, charging_point_id },
  })
}
