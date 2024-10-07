import { api, Api } from "common/services/api"
import { ChargePointsSnapshot } from "./types"

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
