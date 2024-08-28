import { api, Api } from "common/services/api"
import { ChargePointsSnapshot } from "./types"

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
